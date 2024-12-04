// Tambahkan interaktivitas lebih dinamis
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('input[type="file"]');
    const submitButton = document.querySelector('button');
    const fileNameDisplay = document.createElement('p');
    fileNameDisplay.style.fontStyle = 'italic';
    fileNameDisplay.style.color = '#555';
    fileInput.parentNode.appendChild(fileNameDisplay);

    // Menampilkan nama file setelah dipilih
    fileInput.addEventListener('change', (event) => {
        const fileName = event.target.files[0]?.name;
        if (fileName) {
            fileNameDisplay.textContent = `File yang diunggah: ${fileName}`;
        } else {
            fileNameDisplay.textContent = 'Pilih file untuk mengunggah.';
        }
    });

    // Validasi saat tombol submit ditekan
    submitButton.addEventListener('click', (event) => {
        if (!fileInput.value) {
            event.preventDefault();
            alert("Harap pilih file terlebih dahulu!");
        }
    });
});
