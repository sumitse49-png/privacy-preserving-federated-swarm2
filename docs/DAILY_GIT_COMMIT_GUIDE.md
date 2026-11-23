# Daily Git Commit & Collaborative Workflow Guide
**Zaalima Development Pvt. Ltd. — Engineering Team Standard Operating Procedures**  
**Project 2: Privacy-Preserving Federated Swarm Intelligence**  

---

## 1. Collaborative Branch Strategy

As mandated by Zaalima Development SOP Version 1.1, each member must commit directly to their **dedicated feature branch** and never push unfinished code directly to `main`.

### Dedicated Team Branches:
- **Sumeet (Team Lead):** `sumeet/fhe-cryptography-core`
- **Janvhi (Data & Edge):** `janvhi/edge-network-data`
- **Sanskar (Privacy & BFT):** `sanskar/byzantine-dp-dashboard`

---

## 2. Daily Developer Workflow (Commands Reference)

### Step 1: Switch to Your Dedicated Branch
```bash
# For Sumeet:
git checkout sumeet/fhe-cryptography-core

# For Janvhi:
git checkout janvhi/edge-network-data

# For Sanskar:
git checkout sanskar/byzantine-dp-dashboard
```

### Step 2: Stage and Review Your Day's Implementation
```bash
# View modified files
git status

# Stage specific changes
git add src/crypto/fhe_engine.py
# Or stage corresponding daily progress file:
git add docs/sumeet_day_12_progress.md
```

### Step 3: Commit with Conventional Semantic Messages
Format: `<type>(<scope>): <concise active-voice description>`  
Types: `feat`, `fix`, `test`, `docs`, `chore`, `ci`, `refactor`

```bash
git commit -m "feat(crypto): implement vector encryption and ciphertext representation"
```

### Step 4: Periodic Rebase & Merge to Main (Led by Sumeet)
```bash
# Switch to main branch
git checkout main
git pull origin main

# Merge feature branch preserving branch history (No Fast-Forward)
git merge sumeet/fhe-cryptography-core --no-ff -m "merge: integrate 'sumeet/fhe-cryptography-core' into main"
git merge janvhi/edge-network-data --no-ff -m "merge: integrate 'janvhi/edge-network-data' into main"
git merge sanskar/byzantine-dp-dashboard --no-ff -m "merge: integrate 'sanskar/byzantine-dp-dashboard' into main"
```

---

## 3. Mandatory Review Checklist

### 10-Day Mid-Review Verification
Verify at least 10 different calendar days have commits prior to the 23rd:
```bash
git log --format="%ad" --date=short | sort -u | wc -l
```

### 20-Day Final Review Verification
Verify that 20 consecutive days have active commits from the team:
```bash
git log --graph --oneline --decorate --all
```
