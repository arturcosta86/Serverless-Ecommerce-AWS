document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("produtos-container");

  if (container) {
    const produtosDisponiveis = [
      {
        nome: "Caneca Personalizada",
        preco: 49.9,
        imagem: "../assets/caneca.png",
      },
      {
        nome: "Notebook Gamer",
        preco: 149.9,
        imagem: "../assets/macbook.png",
      },
      {
        nome: "Porsche",
        preco: 1500.0,
        imagem: "../assets/porsche.png",
      },
    ];

    produtosDisponiveis.forEach((produto, index) => {
      const div = document.createElement("div");
      div.className = "produto";
      div.innerHTML = `
        <input type="checkbox" id="produto-${index}" value="${produto.nome}">
        <img src="${produto.imagem}" alt="${produto.nome}">
        <div class="produto-info">
          <strong>${produto.nome}</strong>
          <span>R$ ${produto.preco.toFixed(2)}</span>
        </div>
      `;
      container.appendChild(div);
    });
  } else {
    console.error('Elemento com o ID "produtos-container" não encontrado.');
  }
});

function fazerPedido() {
  const checkboxes = document.querySelectorAll(
    "input[type='checkbox']:checked"
  );
  if (checkboxes.length === 0) {
    alert("Por favor, selecione pelo menos um produto.");
    return;
  }

  const selecionados = Array.from(checkboxes).map((cb) => cb.value);
  const produtosParam = selecionados.map(encodeURIComponent).join(",");

  window.location.href = `/pages/revisar-pedido.html?produtos=${produtosParam}`;
}
