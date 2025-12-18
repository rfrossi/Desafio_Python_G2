// array global de receitas
const recipes = [];

// índice da receita atualmente editada
let currentRecipeIndex = null;

// seleção dos elementos
const addButton = document.getElementById("add-recipe");
const cardsDiv = document.getElementById("cards");
const editor = document.getElementById("editor");

const titleInput = document.getElementById("title-input");
const ingredientsInput = document.getElementById("ingredients-input");
const instructionsInput = document.getElementById("instructions-input");
const deleteButton = document.getElementById("delete-recipe");

// cria uma nova receita ao clicar no "+"
addButton.addEventListener("click", function () {

  // índice da nova receita será o tamanho atual do array
  const index = recipes.length;

  // adiciona objeto da receita no array
  recipes.push({
    title: "Sem Título",
    ingredients: "",
    instructions: ""
  });

  // cria o card visual
  const card = document.createElement("div");
  card.className = "card";
  card.innerText = "Sem Título";

  // armazena o índice da receita no card
  card.dataset.index = index;

  // evento de clique no card
  card.addEventListener("click", function () {
    const index = Number(this.dataset.index);
    openEditor(index);
  });

  // adiciona o card na lista
  cardsDiv.appendChild(card);
});

// abre o modo de edição
function openEditor(index) {

  // atualiza o índice atual
  currentRecipeIndex = index;

  // remove destaque de todos os cards
  const allCards = document.querySelectorAll(".card");
  for (const card of allCards) {
    card.classList.remove("active");
  }

  // destaca o card atual
  const activeCard = document.querySelector(
    `[data-index="${index}"]`
  );
  activeCard.classList.add("active");

  // preenche os campos com os dados da receita
  titleInput.value = recipes[index].title;
  ingredientsInput.value = recipes[index].ingredients;
  instructionsInput.value = recipes[index].instructions;

  // mostra o editor
  editor.style.display = "block";
}

// atualiza o título em tempo real
titleInput.addEventListener("input", function () {

  // atualiza o título no array
  recipes[currentRecipeIndex].title = titleInput.value;

  // atualiza o texto do card
  const card = document.querySelector(
    `[data-index="${currentRecipeIndex}"]`
  );
  card.innerText = titleInput.value;
});

// salva ingredientes
ingredientsInput.addEventListener("input", function () {
  recipes[currentRecipeIndex].ingredients = ingredientsInput.value;
});

// salva modo de preparo
instructionsInput.addEventListener("input", function () {
  recipes[currentRecipeIndex].instructions = instructionsInput.value;
});

// deleta a receita atual
deleteButton.addEventListener("click", function () {

  // remove a receita do array
  recipes.splice(currentRecipeIndex, 1);

  // remove o card correspondente
  const cardToRemove = document.querySelector(
    `[data-index="${currentRecipeIndex}"]`
  );
  cardToRemove.remove();

  // corrige os data-index dos cards seguintes
  const allCards = document.querySelectorAll(".card");
  for (const card of allCards) {
    if (Number(card.dataset.index) > currentRecipeIndex) {
      card.dataset.index = Number(card.dataset.index) - 1;
    }
  }

  // fecha o editor
  editor.style.display = "none";
  currentRecipeIndex = null;
});