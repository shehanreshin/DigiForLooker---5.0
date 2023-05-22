function runAperi(image) {
    const image_path = image;  // Set the image path
    const url = '/aperi';  // Flask route for the function

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `image_path=${image_path}`,
    })
    .then(response => response.json())
    .then(data => {
        // Process the result data
        window.open(data, '_blank');
    })
    .catch(error => {
        // Handle any errors
        console.error(error);
    });
}