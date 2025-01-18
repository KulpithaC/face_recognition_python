function setupFilePreview(inputId, previewId, placeholderId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  const placeholder = document.getElementById(placeholderId);

  input.addEventListener("change", function (e) {
    const file = e.target.files[0];
    if (file) {
      preview.querySelector(".filename-text").textContent = file.name;
      preview.classList.remove("hidden");
      placeholder.classList.add("hidden");
    }
  });
}

// Setup file previews
setupFilePreview("registerInput", "registerPreview", "registerPlaceholder");
setupFilePreview("compareInput", "comparePreview", "comparePlaceholder");

function setupDragAndDrop(inputId) {
  const dropZone = document.querySelector(
    `label[for="${inputId}"]`
  ).parentElement;

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });

  function highlight(e) {
    dropZone.classList.add("border-blue-500", "bg-blue-50");
  }

  function unhighlight(e) {
    dropZone.classList.remove("border-blue-500", "bg-blue-50");
  }

  dropZone.addEventListener("drop", handleDrop, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    const input = document.getElementById(inputId);
    input.files = files;
    input.dispatchEvent(new Event("change"));
  }
}

// Setup drag and drop for both upload zones
setupDragAndDrop("registerInput");
setupDragAndDrop("compareInput");

function addImageToList(name, url) {
  const div = document.createElement("div");
  div.className = "image-item relative group";
  div.innerHTML = `
    <div class="image-button w-full px-4 py-2 rounded-lg bg-gray-50 hover:bg-blue-50 text-gray-700 hover:text-blue-600 flex items-center justify-between transition-all duration-200">
      <div class="flex items-center space-x-2">
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span>${name}</span>
      </div>
      <button class="delete-button text-red-500 hover:text-red-700 p-1" onclick="event.stopPropagation(); deleteImage('${name}', this)">
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>`;

  div.querySelector(".image-button").onclick = function (e) {
    if (!e.target.closest(".delete-button")) {
      previewImage(url, name);
    }
  };
  document.getElementById("imageList").appendChild(div);
}

function previewImage(src, name) {
  const preview = document.getElementById("imagePreview");
  preview.innerHTML = `
                <img src="${src}" alt="${name}" class="full-preview rounded-lg">
            `;
}
// Handle image upload
document
  .getElementById("uploadForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
      const response = await fetch("/upload_image", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (result.success) {
        addImageToList(result.image_name, result.image_url);
        showNotification("Image uploaded successfully!", "success");
        // Reset the form and preview
        event.target.reset();
        document.getElementById("registerPreview").classList.add("hidden");
        document
          .getElementById("registerPlaceholder")
          .classList.remove("hidden");
      }
    } catch (error) {
      showNotification("Failed to upload image", "error");
    }
  });

// Handle image comparison
document
  .getElementById("compareForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
      const response = await fetch("/compare_face", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      const resultDiv = document.getElementById("result");
      resultDiv.classList.remove("hidden");
      resultDiv.innerHTML = `
                    <div class="flex items-center justify-center">
                        <svg class="h-5 w-5 ${
                          result.faces.length > 0
                            ? "text-green-500"
                            : "text-red-500"
                        } mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${
                              result.faces.length > 0
                                ? "M5 13l4 4L19 7"
                                : "M6 18L18 6M6 6l12 12"
                            }" />
                        </svg>
                        <span>${
                          result.faces.length > 0
                            ? "Faces detected: " + result.faces.join(", ")
                            : "No faces detected"
                        }</span>
                    </div>
                `;
      // Reset form and preview after successful comparison
      event.target.reset();
      document.getElementById("comparePreview").classList.add("hidden");
      document.getElementById("comparePlaceholder").classList.remove("hidden");
    } catch (error) {
      showNotification("Failed to compare faces", "error");
    }
  });

function showNotification(message, type) {
  const notification = document.createElement("div");
  notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
    type === "success" ? "bg-green-500" : "bg-red-500"
  } text-white transform transition-all duration-500 translate-y-0`;
  notification.textContent = message;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.transform = "translateY(-100%)";
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 500);
  }, 3000);
}

// Fetch initial images
window.onload = async function () {
  try {
    const response = await fetch("/get_uploaded_images");
    const images = await response.json();
    images.forEach((image) => {
      addImageToList(image.name, image.url);
    });
  } catch (error) {
    showNotification("Failed to load images", "error");
  }
};
