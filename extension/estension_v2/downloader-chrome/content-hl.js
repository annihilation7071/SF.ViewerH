console.log("script-start")
console.log("hitomi.la")


setTimeout(() => {
    console.log("wait 1 sec")
    executeScript()
}, 1000)


async function executeScript() {
    let elements_count = -1

    async function find_elements() {
        const galleryItems = document.querySelectorAll(".gallery-content > div")
        if (galleryItems.length > elements_count) {
            elements_count = galleryItems.length
            await wait(500)
            return find_elements()
        } else if (galleryItems.length === elements_count) {
            return galleryItems
        }
    }

    const galleryItems = await find_elements()

    console.log("Elements found: ", galleryItems.length)

    for (const item of galleryItems) {

        console.log(item)
        const link = item.querySelector("a")?.href
        console.log(link)

        if (!link) return
        console.log('cp-0')

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

            console.log('cp-1')

            const {status} = await response.json()

            console.log(status)
            console.log('cp-2')

            if (status === "found") {
                addStatusElement(item, "found", "Downloaded!")
            } else if (status === "deleted") {
                addStatusElement(item, "deleted", "Prevorus deleted!")
            }
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

function wait(millliseconds) {
    return new Promise(resolve => {setTimeout(resolve, millliseconds)})
}