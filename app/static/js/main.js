function showLoadingMessage() {
    var form = document.getElementById('generateForm');
    var previewElements = document.getElementById('preview');
    var loadingMessage = document.getElementById('loadingMessage');

    if (form) {
        form.style.display = 'none';
    }

    if (previewElements) {
        previewElements.style.display = 'none';
    }


    // showing the loading message
    loadingMessage.style.display = 'block';
}

function sendFeedback(feedback, resumeId) {
    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resume_id: resumeId, feedback: feedback })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('feedbackMessage').innerText = 'Thanks for your feedback!';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
