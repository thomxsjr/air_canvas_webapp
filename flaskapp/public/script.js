document.addEventListener('DOMContentLoaded', () => {
    const startDrawingBtn = document.getElementById('start-drawing-btn');

    // Event listener for the Start Drawing button
    startDrawingBtn.addEventListener('click', () => {
        // Send a GET request to the server to start the drawing app
        fetch('/canvas')
            .then(response => {
                if (response.ok) {
                    console.log('Drawing app started!');
                } else {
                    console.error('Failed to start drawing app');
                }
            })
            .catch(error => console.error('Error:', error));
    });
});
