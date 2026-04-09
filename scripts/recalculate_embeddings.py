#!/usr/bin/env python3
"""
recalculate_embeddings.py
--------------------------
Recalcula los embeddings de todos los registros `Tool` en la base de datos.

Uso:
    python recalculate_embeddings.py [--force] [--batch-size N] [--delay S]

Opciones:
    --force         Recalcula aunque el embedding ya exista (por defecto sólo
                    procesa los que están vacíos / NULL).
    --batch-size N  Número de tools a confirmar en cada commit (default: 10).
    --delay S       Segundos de espera entre llamadas a la API (default: 0.5).
    --dry-run       Muestra qué se recalcularía sin hacer ningún cambio.
"""

import sys
import time
import argparse
import traceback

# ---------------------------------------------------------------------------
# Inicializar la app de Flask para tener contexto de BD y configuración
# ---------------------------------------------------------------------------
from app import create_app, db
from app.models import Tool

# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Recalcula los embeddings de todos los Tools en la BD."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Recalcular aunque el embedding ya exista.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        metavar="N",
        help="Herramientas por commit (default: 10).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        metavar="S",
        help="Segundos entre llamadas a la API (default: 0.5).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Muestra qué se recalcularía sin hacer cambios.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    app = create_app()

    with app.app_context():
        # Obtener todos los tools, o sólo los que no tienen embedding
        if args.force:
            tools = Tool.query.order_by(Tool.id).all()
            label = "todos los"
        else:
            tools = (
                Tool.query.filter(
                    (Tool.embedding == None) | (Tool.embedding == "")
                )
                .order_by(Tool.id)
                .all()
            )
            label = "los tools SIN embedding de"

        total = len(tools)
        if total == 0:
            print("✅  No hay tools que procesar. Usa --force para forzar el recálculo de todos.")
            return

        print(f"\n{'='*60}")
        print(f"  Recalculando embeddings de {label} {total} tool(s)")
        if args.dry_run:
            print("  *** MODO DRY-RUN: no se guardarán cambios ***")
        print(f"  Batch size : {args.batch_size}")
        print(f"  Delay API  : {args.delay}s")
        print(f"{'='*60}\n")

        ok_count = 0
        fail_count = 0
        skipped_count = 0
        failed_tools = []

        for idx, tool in enumerate(tools, start=1):
            prefix = f"[{idx:>4}/{total}]"

            if args.dry_run:
                print(f"{prefix} 🔍  (dry-run) Tool #{tool.id}: {tool.name}")
                skipped_count += 1
                continue

            try:
                success = tool.generate_embedding()

                if success:
                    ok_count += 1
                    print(f"{prefix} ✅  Tool #{tool.id}: {tool.name}")
                else:
                    fail_count += 1
                    failed_tools.append((tool.id, tool.name, "generate_embedding() returned False"))
                    print(f"{prefix} ❌  Tool #{tool.id}: {tool.name}  → generate_embedding() falló")

            except Exception as exc:
                fail_count += 1
                err_msg = str(exc)
                failed_tools.append((tool.id, tool.name, err_msg))
                print(f"{prefix} ❌  Tool #{tool.id}: {tool.name}  → {err_msg}")
                traceback.print_exc()

            # Commit parcial cada `batch_size` registros exitosos
            if ok_count > 0 and ok_count % args.batch_size == 0:
                try:
                    db.session.commit()
                    print(f"          💾  Commit parcial ({ok_count} guardados hasta ahora)…")
                except Exception as commit_exc:
                    print(f"          ⚠️   Error en commit parcial: {commit_exc}")
                    db.session.rollback()

            # Pequeña pausa para no saturar la API
            if args.delay > 0:
                time.sleep(args.delay)

        # Commit final de los registros restantes
        if not args.dry_run and ok_count > 0:
            try:
                db.session.commit()
                print("\n💾  Commit final realizado.\n")
            except Exception as commit_exc:
                print(f"\n⚠️   Error en el commit final: {commit_exc}")
                db.session.rollback()

        # ---------------------------------------------------------------------------
        # Resumen
        # ---------------------------------------------------------------------------
        print(f"\n{'='*60}")
        print("  RESUMEN")
        print(f"{'='*60}")
        print(f"  Total procesados : {total}")
        if args.dry_run:
            print(f"  (dry-run, sin cambios)")
        else:
            print(f"  Exitosos         : {ok_count}")
            print(f"  Fallidos         : {fail_count}")

        if failed_tools:
            print(f"\n  Tools con error:")
            for tid, tname, reason in failed_tools:
                print(f"    • #{tid} '{tname}': {reason}")

        print(f"{'='*60}\n")

        # Código de salida != 0 si hubo fallos
        if fail_count > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
