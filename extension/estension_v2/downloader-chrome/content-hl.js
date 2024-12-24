    console.log("hitomi.la")

if (document.readyState === "loading") {
    console.log("test-1");
} else {
    console.log("test-2");
    setTimeout(() => {
        console.log("wait 5 sec")
        executeScript()
    }, 2000)
}

function executeScript() {
    console.log("script start")
    const galleryItems = document.querySelectorAll(".gallery-content > div")
    console.log("Elements found: ", galleryItems.length);

    galleryItems.forEach(async (item) => {

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

            if (status === "success") {
                item.classList.add("success-style")
                addStatusElement(item, "found", "Succes!")
            } else if (status === "error") {
                item.classList.add("error-style")
                addStatusElement(item, "", "Error!")
            }
        } catch (error) {
            console.error("Error!", error)
        }
    })
}

function addStatusElement(parent, style, text) {
    const statusElement = document.createElement("div")
    statusElement.className = `status ${style}`
    statusElement.textContent = text
    parent.appendChild(statusElement)
}