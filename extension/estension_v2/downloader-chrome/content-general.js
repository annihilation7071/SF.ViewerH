async function isServerAvailable(url) {
    try {

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({url: "test"})
        })

        return response.ok; // true
    } catch (error) {
        return false;
    }
}

function wait(milliseconds) {
    return new Promise(resolve => {setTimeout(resolve, milliseconds)})
}