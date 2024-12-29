console.log("script-start")
console.log("hitomi.la")

window.addEventListener("load", async () => {
    console.log("Page loaded, check server available...")

    const serverUrl = "http://127.0.0.1:1707/get-status"
    const serverAvailable = await isServerAvailable(serverUrl)

    if (!serverAvailable) {
        console.log("server not available")
        return
    }

    console.log("server available")
    console.log("waiting for elements")

    await checkElements()

    const interval = 5000
    const timeout = 20000
    const startTime = Date.now()

    const intervalId = setInterval(async () => {
        console.log("checking elements")
        if (Date.now() - startTime >= timeout) {
            clearInterval(intervalId)
        }
        await checkElements()
    }, interval)

    async function checkElements() {
        const elements = await waitForElements(".gallery-content > div:not(.checked)", 500, 5000)
        if (elements) {
            console.log("Elements found: " + elements.length)
            await executeScript(elements)
        } else {
            console.log("Elements not found")
        }
    }

})

async function executeScript(galleryItems) {

    for (const item of galleryItems) {

        console.log(item)
        const link = item.querySelector("a")?.href
        console.log(link)

        if (!link) return

        try {
            const response = await fetch("http://127.0.0.1:1707/get-status", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({url: link})
            })

            console.log(response)

            if (!response.ok) {
                console.error(`Error: ${response.statusText}`)
                return
            }

            const {status} = await response.json()

            console.log(status)

            if (status === "found") {
                addStatusElement(item, "found", "Downloaded!")
            } else if (status === "deleted") {
                addStatusElement(item, "deleted", "Prevorus deleted!")
            }
            item.classList.add("checked")
        } catch (error) {
            console.error("Error!", error)
        }
    }
}

function addStatusElement(parent, style, text) {
    const statusElement = document.createElement("div")
    statusElement.className = `status ${style}`

    const statusText = document.createElement("div")
    statusText.className = "status-text"
    statusText.textContent = text

    statusElement.appendChild(statusText)
    parent.appendChild(statusElement)
}



