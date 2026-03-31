(function () {
    var STORAGE_KEY = 'devdock_saved_tools';

    function getSavedTools() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    }

    function saveTools(tools) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(tools));
    }

    function isSaved(toolId, tools) {
        return tools.some(function (tool) {
            return String(tool.id) === String(toolId);
        });
    }

    function updateButtonState(button, saved) {
        var icon = button.querySelector('.material-symbols-outlined');
        var label = button.querySelector('.save-tool-label');

        if (icon) {
            icon.textContent = 'bookmark';
            if (saved) {
                icon.style.fontVariationSettings = "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24";
            } else {
                icon.style.fontVariationSettings = "'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24";
            }
            icon.classList.toggle('text-yellow-400', saved);
            icon.classList.toggle('text-on-surface-variant', !saved);
        }

        button.title = saved ? 'Quitar de guardados' : 'Guardar';

        if (label) {
            label.textContent = saved ? 'Guardado' : 'Guardar';
        }
    }

    function removeTool(toolId, tools) {
        return tools.filter(function (tool) {
            return String(tool.id) !== String(toolId);
        });
    }

    function addTool(button, tools) {
        tools.push({
            id: button.dataset.toolId,
            name: button.dataset.toolName,
            url: button.dataset.toolUrl,
        });
        return tools;
    }

    function initSaveButtons() {
        var buttons = document.querySelectorAll('.save-tool-btn');
        if (!buttons.length) {
            return;
        }

        var savedTools = getSavedTools();

        buttons.forEach(function (button) {
            if (button.dataset.saveBound === '1') {
                return;
            }

            var toolId = button.dataset.toolId;
            updateButtonState(button, isSaved(toolId, savedTools));
            button.dataset.saveBound = '1';

            button.addEventListener('click', function () {
                var currentTools = getSavedTools();
                var exists = isSaved(toolId, currentTools);

                if (exists) {
                    saveTools(removeTool(toolId, currentTools));
                    updateButtonState(button, false);
                    return;
                }

                saveTools(addTool(button, currentTools));
                updateButtonState(button, true);
            });
        });
    }

    window.initToolSaveButtons = initSaveButtons;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSaveButtons);
    } else {
        initSaveButtons();
    }
})();
