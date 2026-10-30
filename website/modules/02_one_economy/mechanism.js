"use strict";
// A conceptual navigation map. No numerical model, simulation or statistic is
// evaluated here; all experiments below still use the saved Python results.
(() => {
  const map = document.getElementById("mechanism-map");
  if (!map) return;
  const order = ["households", "labor", "firms", "competition", "demand", "composite"];
  const nodes = {
    households: {title: "Households supply labor.", text: "A higher wage raises labor supplied.", relation: "Wage W → labor supplied L<sup>s</sup>"},
    labor: {title: "Every unit of labor has a use.", text: "Production labor and fixed operating labor together must equal labor supplied.", relation: "Σ (production labor + fixed labor) = labor supplied"},
    firms: {title: "Firms differ in productivity.", text: "Firms use production inputs and fixed operating labor; capital has a given rental price R.", relation: "Firm employment = production labor + fixed labor"},
    competition: {title: "Market shares affect markups.", text: "Cournot quantity competition links each firm's share to its demand elasticity and markup.", relation: "Shares ↔ elasticities ↔ markups ↔ prices"},
    demand: {title: "Prices allocate demand.", text: "Relative prices allocate aggregate demand across sectors and among firms within each sector.", relation: "Aggregate demand → sectors → firms"},
    composite: {title: "Consumers demand goods.", text: "Relative prices allocate consumer demand across sectors and firms.", relation: "Composite good Y · price P = 1"}
  };
  const stories = {
    economy: {order, overrides: {}},
    productivity: {
      order: ["firms", "competition", "demand", "labor", "composite", "households"],
      overrides: {
        firms: {title: "Start with productivity.", text: "Keep the same underlying shocks; changing dispersion transforms firms’ productivity levels.", relation: "Productivity → production requirements"},
        competition: {title: "The competitive balance changes.", text: "Recompute shares, demand elasticities and markups for the operating firms.", relation: "Productivity ↔ shares ↔ markups"},
        demand: {title: "Demand is allocated again.", text: "The resulting relative prices determine how demand is divided across sectors and firms.", relation: "Relative prices → sector and firm demand"},
        labor: {title: "The labor market must still clear.", text: "Recompute production and fixed labor together with output and the wage.", relation: "Labor used = labor supplied"},
        composite: {title: "Inspect the solved outcome.", text: "Feedback through demand, wages and exit makes the aggregate response an equilibrium result.", relation: "Use the numerical experiment below to see the outcome."},
        households: {title: "Labor supply responds to the wage.", text: "The wage feeds back into households' labor supplied.", relation: "W → labor supplied"}
      }
    },
    fixed: {
      order: ["firms", "labor", "competition", "demand", "composite", "households"],
      overrides: {
        firms: {title: "Start with fixed operating labor.", text: "An operating firm needs fixed labor in addition to its production labor.", relation: "Fixed labor per operating firm = φ"},
        labor: {title: "Fixed labor uses the same supply.", text: "For a given operating set, changing φ changes the fixed labor requirement.", relation: "Production labor + fixed labor = labor supplied"},
        competition: {title: "Profit and exit feed back.", text: "The exit rule can change the operating set; shares, markups and prices are then solved again.", relation: "Profit → exit rule → new operating set"},
        demand: {title: "Demand follows the new prices.", text: "Recompute demand using the prices and firms remaining in each sector.", relation: "New operating set ↔ prices ↔ demand"},
        composite: {title: "Read the full equilibrium effect.", text: "Output, wages, production labor and the operating set can all adjust.", relation: "Use the numerical experiment below to compare the rules."},
        households: {title: "The wage closes the labor link.", text: "Labor supplied responds to the resulting wage.", relation: "W → labor supplied"}
      }
    }
  };
  let story = "economy";
  let active = "households";
  const nodeButtons = document.querySelectorAll("[data-node]");
  const storyButtons = document.querySelectorAll("[data-story]");
  const previous = document.getElementById("mechanism-prev");
  const next = document.getElementById("mechanism-next");
  nodeButtons.forEach(button => {
    const hint = document.createElement("span");
    hint.className = "node-detail";
    hint.setAttribute("aria-hidden", "true");
    button.appendChild(hint);
  });
  function render() {
    const sequence = stories[story].order;
    const position = sequence.indexOf(active);
    const detail = stories[story].overrides[active] || nodes[active];
    map.dataset.active = active;
    map.dataset.story = story;
    document.getElementById("mechanism-position").textContent = ["01", "02", "03", "04", "05", "06"][position] + " / 06";
    document.getElementById("mechanism-node-title").textContent = detail.title;
    document.getElementById("mechanism-explanation").textContent = detail.text;
    document.getElementById("mechanism-relation").innerHTML = detail.relation;
    nodeButtons.forEach(button => {
      button.setAttribute("aria-pressed", button.dataset.node === active ? "true" : "false");
      button.querySelector(".node-detail").textContent = button.dataset.node === active ? detail.text : "";
    });
    storyButtons.forEach(button => button.setAttribute("aria-pressed", button.dataset.story === story ? "true" : "false"));
    document.querySelectorAll("[data-link]").forEach(link => link.classList.toggle("is-active", link.dataset.link.split(" ").includes(active)));
    previous.disabled = position === 0;
    next.innerHTML = position === sequence.length - 1 ? 'Start again <span aria-hidden="true">↺</span>' : 'Next <span aria-hidden="true">→</span>';
  }
  nodeButtons.forEach(button => button.addEventListener("click", () => { active = button.dataset.node; render(); }));
  storyButtons.forEach(button => button.addEventListener("click", () => { story = button.dataset.story; active = stories[story].order[0]; render(); }));
  previous.addEventListener("click", () => { const sequence = stories[story].order; active = sequence[sequence.indexOf(active) - 1]; render(); });
  next.addEventListener("click", () => { const sequence = stories[story].order; active = sequence[sequence.indexOf(active) + 1] || sequence[0]; render(); });
  render();
})();
