function showLoadingMessage() {
    var form = document.getElementById('generateForm');
    var loadingMessage = document.getElementById('loadingMessage');

    // hide the form
    form.style.display = 'none';

    // showing the loading message
    loadingMessage.style.display = 'block';
}