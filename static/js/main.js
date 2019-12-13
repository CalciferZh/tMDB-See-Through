// global variables
let DataLoader = null;
let Layout = null;

// entry
window.onload = function() {
  DataLoader = new DataLoaderClass();
  DataLoader.get_data();
  Layout = new LayoutClass();
};
