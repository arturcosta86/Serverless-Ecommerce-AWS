// 🔧 Substitua pela URL do seu endpoint do API Gateway
const API_URL = "https://pev6keanr8.execute-api.us-east-1.amazonaws.com/dev";

const urlParams = new URLSearchParams(window.location.search);
let produtosSelecionados = [];

if (urlParams.has("produtos")) {
  produtosSelecionados = urlParams
    .get("produtos")
    .split(",")
    .map(decodeURIComponent);
} else {
  produtosSelecionados = urlParams
    .getAll("produto")
    .map(decodeURIComponent);
}

const produtosDisponiveis = [
  {
    nome: "Caneca Personalizada",
    preco: 49.9,
    imagem: "../assets/caneca.png"
  },
  {
    nome: "Notebook Gamer",
    preco: 149.9,
    imagem: "../assets/macbook.png"
  },
  {
    nome: "Porsche",
    preco: 1500.0,
    imagem: "../assets/porsche.png"
  }
];

const normalizar = (str) =>
  str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

const container = document.getElementById("resumo-pedido");

const encontrados = produtosDisponiveis.filter((p) =>
  produtosSelecionados.some(
    (selecionado) => normalizar(selecionado) === normalizar(p.nome)
  )
);

let total = 0;

if (encontrados.length === 0) {
  container.innerHTML = "<p>Nenhum produto encontrado.</p>";
} else {
  encontrados.forEach((prod) => {
    total += prod.preco;
    const div = document.createElement("div");
    div.className = "produto";
    div.innerHTML = `
      <img src="${prod.imagem}" alt="${prod.nome}" />
      <div>
        <h2>${prod.nome}</h2>
        <p>R$ ${prod.preco.toFixed(2)}</p>
      </div>
    `;
    container.appendChild(div);
  });

  const totalDiv = document.createElement("div");
  totalDiv.innerHTML = `<h3>Total: R$ ${total.toFixed(2)}</h3>`;
  container.appendChild(totalDiv);
}

document.getElementById("finalizar-pedido").addEventListener("click", () => {
  fetch(`${API_URL}/pedidos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      produtos: encontrados.map((p) => p.nome),
      total: total,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("Resposta recebida da API:", data);

      let respostaFinal = data;
      if (typeof data.body === "string") {
        try {
          respostaFinal = JSON.parse(data.body);
        } catch (e) {
          console.error("Erro ao fazer parse do body:", e);
        }
      }

      const pedidoId = respostaFinal.pedidoId;

      if (pedidoId) {
        alert("Pedido realizado com sucesso!");

        localStorage.setItem("produtosPedido", JSON.stringify(encontrados));
        localStorage.setItem("totalPedido", total.toFixed(2));
        localStorage.setItem("pedidoId", pedidoId);

        window.location.href = `/pages/pedido.html?pedidoId=${pedidoId}`;
      } else {
        alert("Pedido iniciado, mas o ID não foi retornado.");
      }
    })
    .catch((err) => {
      console.error("Erro ao iniciar pedido:", err);
      alert("Erro ao iniciar o pedido. Tente novamente.");
    });
});