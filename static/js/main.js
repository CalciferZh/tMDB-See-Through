// global variables
let DataLoader = null;
let Layout = null;

// entry
window.onload = function() {
  DataLoader = new DataLoaderClass();
  Layout = new LayoutClass();
  DataLoader.get_data();
};
