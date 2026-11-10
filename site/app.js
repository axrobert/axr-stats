const ranks = [
  { name: "Novice", hours: 0, image: "01-novice.png" },
  { name: "Explorer", hours: 25, image: "02-explorer.png" },
  { name: "Artisan", hours: 100, image: "03-artisan.png" },
  { name: "Specialist", hours: 250, image: "04-specialist.png" },
  { name: "Veteran", hours: 500, image: "05-veteran.png" },
  { name: "Master", hours: 1000, image: "06-master.png" },
  { name: "Legend", hours: 2500, image: "07-legend.png" },
];

const rankGrid = document.querySelector("#rank-grid");

if (rankGrid) {
  ranks.forEach(({ name, hours, image }, index) => {
    const card = document.createElement("article");
    card.className = "rank-card";

    const art = document.createElement("img");
    art.src = "assets/badges/" + image;
    art.alt = "Emblema AXR " + name;
    art.loading = "lazy";
    art.width = 153;
    art.height = 168;

    const tier = document.createElement("span");
    tier.className = "idx";
    tier.textContent = "TIER " + String(index + 1).padStart(2, "0");

    const title = document.createElement("strong");
    title.textContent = name;

    const requirement = document.createElement("small");
    requirement.textContent = hours.toLocaleString("pt-BR") + " horas registradas";

    card.append(art, tier, title, requirement);
    rankGrid.append(card);
  });
}
