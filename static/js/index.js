function myFunction() {
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  ul = document.getElementById("myUL");
  li = ul.getElementsByTagName("li");

  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}

// Js for product gallery

let ProductImg = document.getElementById("productImg");

let SmallImg = document.getElementsByClassName("small-img");

SmallImg[0].onclick = function () {
  ProductImg.src = SmallImg[0].src;
};

SmallImg[1].onclick = function () {
  ProductImg.src = SmallImg[1].src;
};

SmallImg[2].onclick = function () {
  ProductImg.src = SmallImg[2].src;
};

// Product

let productInCard = [];

const parentElement = document.querySelector("#buyItems");
