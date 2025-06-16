chrome.runtime.onInstalled.addListener(function () {
      chrome.tabs.create({
            url: 'https://github.com/HT3301601278/FigmaCN'
      });
})
