const fs = require("fs");
const path = require("path");

const dir = "./content/blog";
const files = fs.readdirSync(dir);

const posts = files.map(file => {
  const content = fs.readFileSync(path.join(dir, file), "utf8");

  const meta = content.match(/---([\s\S]*?)---/)[1];

  const get = (key) =>
    meta.split("\n").find(l => l.includes(key))?.split(":")[1]?.trim();

  return {
    title: get("title"),
    category: get("category"),
    author: get("author"),
    excerpt: get("excerpt"),
    body: content.split("---")[2]
  };
});

fs.writeFileSync(
  "./content/blog/index.json",
  JSON.stringify(posts, null, 2)
);