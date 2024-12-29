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

function waitForElements(selector, interval = 500, timeout = 20000) {
    return new Promise((resolve) => {
        const startTime = Date.now()

        const timer = setInterval(() => {
            const elements = document.querySelectorAll(selector)
            if (elements.length > 0) {
                clearInterval(timer)
                resolve(elements)
            } else if (Date.now() - startTime > timeout) {
                clearInterval(timer)
                resolve(null)
            }
        }, interval)
    })
}