const scrollRoot = document.querySelector("#scrollRoot");
const pages = [...document.querySelectorAll(".page")];
const navLinks = [...document.querySelectorAll(".nav-list a")];
const pageIndicator = document.querySelector("#pageIndicator");

let isScrolling = false;
let scrollTimeout = null;

function getCurrentPageIndex() {
  const scrollTop = scrollRoot.scrollTop;
  const viewMid = scrollTop + scrollRoot.clientHeight * 0.4;
  let current = 0;

  pages.forEach((page, index) => {
    if (page.offsetTop <= viewMid) {
      current = index;
    }
  });

  return current;
}

function updateUI() {
  const index = getCurrentPageIndex();
  const page = pages[index];

  pageIndicator.textContent = `${index + 1} / ${pages.length}`;

  navLinks.forEach((link) => {
    const target = link.dataset.page;
    link.classList.toggle("active", page && page.id === target);
  });
}

function scrollToPage(index) {
  if (index < 0 || index >= pages.length) {
    return;
  }

  isScrolling = true;
  pages[index].scrollIntoView({ behavior: "smooth", block: "start" });

  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(() => {
    isScrolling = false;
    updateUI();
  }, 700);
}

navLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const targetId = link.dataset.page;
    const targetPage = document.getElementById(targetId);
    if (targetPage) {
      targetPage.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});

scrollRoot.addEventListener(
  "scroll",
  () => {
    if (!isScrolling) {
      updateUI();
    }
  },
  { passive: true }
);

window.addEventListener("keydown", (event) => {
  const index = getCurrentPageIndex();

  if (event.key === "ArrowDown" || event.key === "PageDown") {
    event.preventDefault();
    scrollToPage(index + 1);
  } else if (event.key === "ArrowUp" || event.key === "PageUp") {
    event.preventDefault();
    scrollToPage(index - 1);
  } else if (event.key === "Home") {
    event.preventDefault();
    scrollToPage(0);
  } else if (event.key === "End") {
    event.preventDefault();
    scrollToPage(pages.length - 1);
  }
});

let wheelAccum = 0;
let wheelTimer = null;

scrollRoot.addEventListener(
  "wheel",
  (event) => {
    if (Math.abs(event.deltaY) < 30) {
      return;
    }

    wheelAccum += event.deltaY;

    clearTimeout(wheelTimer);
    wheelTimer = setTimeout(() => {
      wheelAccum = 0;
    }, 200);

    const index = getCurrentPageIndex();
    const page = pages[index];
    const scrollTop = scrollRoot.scrollTop;
    const viewBottom = scrollTop + scrollRoot.clientHeight;
    const pageTop = page.offsetTop;
    const pageBottom = pageTop + page.offsetHeight;
    const atTop = scrollTop <= pageTop + 8;
    const atBottom = viewBottom >= pageBottom - 8;

    if (event.deltaY > 0 && atBottom && wheelAccum > 80) {
      event.preventDefault();
      wheelAccum = 0;
      scrollToPage(index + 1);
    } else if (event.deltaY < 0 && atTop && wheelAccum < -80) {
      event.preventDefault();
      wheelAccum = 0;
      scrollToPage(index - 1);
    }
  },
  { passive: false }
);

updateUI();
