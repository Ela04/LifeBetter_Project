/**
 * LifeBetter SaaS - Community Forum Module
 */

/**
 * Inserta un emoji en la posición actual del cursor dentro del textarea del foro.
 * @param {string} emoji 
 */
function addEmoji(emoji) {
    const textarea = document.getElementById('postContent');
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;

    textarea.value = text.substring(0, start) + emoji + text.substring(end);
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
}

/**
 * Muestra u oculta el contenedor del Emoji Picker estilo WhatsApp
 */
function toggleEmojiPicker() {
    const pickerContainer = document.getElementById('emojiPickerContainer');
    if (pickerContainer) {
        pickerContainer.classList.toggle('d-none');
    }
}

/**
 * Confirmación previa antes de eliminar una publicación
 */
function confirmDeletePost(event) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta publicación? Esta acción no se puede deshacer.')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Inicialización de escuchadores de eventos para el Picker de Emojis
document.addEventListener('DOMContentLoaded', () => {
    const picker = document.querySelector('emoji-picker');
    if (picker) {
        picker.addEventListener('emoji-click', event => {
            addEmoji(event.detail.unicode);
        });
    }
});