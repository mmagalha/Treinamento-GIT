Para criar um **Pull Request (PR)** no GitHub, você precisa ter um repositório com pelo menos duas branches (ou um fork) e alterações que deseja propor. Abaixo estão os passos detalhados:

---

## ✅ Pré-requisitos

* Ter um repositório no GitHub (pode ser seu ou de outra pessoa).
* Ter feito alterações em uma **branch diferente da `main`** (ex: `feature/nova-funcionalidade`).
* Ter feito `git push` da branch para o GitHub.

---

## 🔧 Etapas para Criar um Pull Request (PR)

### 🔁 1. Crie uma branch localmente

```bash
git checkout -b minha-nova-feature
# Faça alterações nos arquivos
git add .
git commit -m "Adiciona nova feature"
```

### ☁️ 2. Suba sua branch para o GitHub

```bash
git push origin minha-nova-feature
```

### 🌐 3. Vá até o GitHub

1. Acesse o repositório no navegador.
2. O GitHub mostrará um banner sugerindo a criação de um Pull Request da nova branch.
3. Clique em **“Compare & pull request”**.

---

### ✏️ 4. Preencha os detalhes do PR

* **Title**: um título claro para a mudança (ex: `Adiciona novo formulário de login`).
* **Description**: explique o que foi feito, por quê, e qualquer contexto necessário.
* Confirme que a base está correta:

  * `base: main`
  * `compare: minha-nova-feature`

---

### 📩 5. Clique em **"Create pull request"**

Pronto! Seu PR foi criado. Agora alguém pode:

* Fazer revisão de código
* Comentar
* Solicitar mudanças
* Aprovar
* Fazer o **merge**

---

## 🧪 (Opcional) Usando a linha de comando para abrir o PR

Se você usa a **GitHub CLI (`gh`)**, pode fazer:

```bash
gh pr create --base main --head minha-nova-feature --title "Minha nova feature" --body "Descrição do que foi feito"
```

---
