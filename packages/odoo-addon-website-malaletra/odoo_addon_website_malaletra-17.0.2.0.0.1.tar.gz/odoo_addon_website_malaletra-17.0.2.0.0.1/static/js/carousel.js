(function() {

    // Select the node that will be observed for mutations
    const targetNode = document.querySelector(".s_dynamic_snippet_products");

    // Options for the observer (which mutations to observe)
    const config = { attributes: true, childList: true, subtree: true };

    // Callback function to execute when mutations are observed
    const hideLoaderCallback = (mutationList, observer) => {
        let loader = document.querySelector(".loader-container")
        loader.innerHTML = ''
        observer.disconnect();
    };

    // Create an observer instance linked to the callback function
    const observer = new MutationObserver(hideLoaderCallback);

    // Start observing the target node for configured mutations
    observer.observe(targetNode, config);

 })()