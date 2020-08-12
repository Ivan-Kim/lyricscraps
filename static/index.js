/**
 * Sample JavaScript code for youtube.search.list
 * See instructions for running APIs Explorer code samples locally:
 * https://developers.google.com/explorer-help/guides/code_samples#javascript
 */

const searchform = document.getElementById("searchform");
const searchbar = document.getElementById("searchbar");

const player = document.getElementById("player");
const video = document.getElementById("video");

const originalBox = document.getElementById("original");
const translatedBox = document.getElementById("translated");

const readme = document.getElementById("readme");

let songTitle;

searchform.addEventListener("submit", (e) => {
  e.preventDefault();
  readme.remove();
  songTitle = searchbar.value;
  // first search youtube with the submitted query
  fetch(`search/${songTitle}`)
    .then((response) => response.json())
    .then((result) => {
      let link = result["link"];
      let title = result["title"];

      // change video display
      video.removeAttribute("hidden");
      video.setAttribute("src", link);

      // google search title of the video (as to explictly search with japanese characters)
      fetch(`update/${title}`)
        .then((response) => response.json())
        .then((result) => {
          original = result["original"];
          translated = result["translated"];
          originalBox.innerText = original;
          translatedBox.innerText = translated;
        });
    });
  searchbar.value = "";
});
