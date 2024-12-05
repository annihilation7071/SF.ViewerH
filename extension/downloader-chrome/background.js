chrome.action.onClicked.addListener ((tab) => {
    if (tab.url) {
        const currentUrl = tab.url

        fetch("http://127.0.0.1:1707/load", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: currentUrl })
        })
        .then(response => {
            if (response.ok) {
                console.log("URL sent!")
            } else {
                console.log("ERROR:", response.statusText)
            }
        })
        .catch(error => {
            console.log("ERROR:", error)
        })
    } else {
        console.error("URL unavailable")
    }
})