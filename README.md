# Wadokei
Poniżej jest którka instrukacja obsługi git'a. <br /> 
Nie wiem jak będziemy pracować, ale najlepiej jakby każdy pracował na własnym branchu, jeżeli każdy coś innego będzie robił. Można też podzielić na np. backend i forntend, do dogadania. <br /> 
Oczywiście można korzystać z po prostu z githuba w przeglądarce, jednak git jest zapewne szybszy. <br /> 
Pamiętajcie, żeby nie commitować każdej zmiany ustawienia przecinka, tylko jakieś większe rzeczy - nie ma sensu co chwilę aktualizować, bo to sprawia problem innym, którzy korzystają z repo. <br /> 

Co do kodów, to piszcie po angielsku i z komentarzami, przykład w time_and_sun.py. Ofc swój kod można wrzuić w Claude/Chat z poleceniem typu "translate to english, add comments, fix foramatting"

#Link do arkusza testowego
https://sggwpl-my.sharepoint.com/:x:/g/personal/s211023_sggw_edu_pl/EQ6HWAF4E7FIkiIL0NvcbyoBf3Alt7RGVhKxA5kDoySnpw?e=ExRShz

# Git - Instrukcja obsługi

Ta instrukcja zawiera podstawowe informacje dotyczące korzystania z systemu kontroli wersji Git w środowisku lokalnym.

## Spis treści
- [Klonowanie repozytorium](#klonowanie-repozytorium)
- [Tworzenie własnego brancha](#tworzenie-własnego-brancha)
- [Dodawanie zmian](#dodawanie-zmian)
- [Zatwierdzanie zmian (commit)](#zatwierdzanie-zmian-commit)
- [Publikowanie zmian (push)](#publikowanie-zmian-push)
- [Pobieranie zmian (pull)](#pobieranie-zmian-pull)
- [Łączenie branchy (merge)](#łączenie-branchy-merge)
- [Rozwiązywanie konfliktów](#rozwiązywanie-konfliktów)
- [Przydatne komendy](#przydatne-komendy)

## Klonowanie repozytorium

Aby rozpocząć pracę z istniejącym repozytorium, należy je sklonować:

```bash
git clone <adres_repozytorium>
```

Przykład:
```bash
git clone https://github.com/username/nazwa-repo.git
```

Po sklonowaniu, wejdź do katalogu projektu:
```bash
cd nazwa-repo
```

## Tworzenie własnego brancha

Dobra praktyka to tworzenie oddzielnych gałęzi (branchy) dla każdej nowej funkcjonalności lub poprawki.

1. Upewnij się, że masz najnowszą wersję głównej gałęzi:
```bash
git checkout main
git pull
```

2. Utwórz nową gałąź:
```bash
git checkout -b nazwa-nowej-galezi
```

Na przykład:
```bash
git checkout -b feature/login-page
```

## Dodawanie zmian

Po wprowadzeniu zmian w kodzie, możesz sprawdzić status zmian:

```bash
git status
```

Aby dodać wszystkie zmodyfikowane pliki do kolejki zmian:
```bash
git add .
```
Tutaj sugestia, żeby dodawac pliki raczej po nazwach, ewentualnie stworzyć plik gitignore:
W głównym katalogu repozytorium stwórz plik .gitignore
Dodaj zawartość, którą git zignoruje przy wykonywaniu komendy 
```bash 
git add .
```
Zawartość dodać można przy użyciu
```txt
# Ignoruj pliki tymczasowe
*.tmp

# Ignoruj katalog z plikami budowania
/build/

# Ignoruj konkretny plik
config.json
```

Aby dodać konkretny plik:
```bash
git add sciezka/do/pliku.txt
```

## Zatwierdzanie zmian (commit)

Gdy dodałeś pliki do kolejki zmian, zatwierdź je:

```bash
git commit -m "Krótki opis wprowadzonych zmian"
```

Dobra praktyka to pisanie zwięzłych, ale informatywnych wiadomości commit.

## Publikowanie zmian (push)

Aby opublikować zatwierdzone zmiany w zdalnym repozytorium:

```bash
git push origin nazwa-twojej-galezi
```

Przykład:
```bash
git push origin feature/login-page
```

Przy pierwszym pushu możesz użyć flagi `-u` aby ustawić upstream:
```bash
git push -u origin nazwa-twojej-galezi
```

## Pobieranie zmian (pull)

Aby pobrać najnowsze zmiany z repozytorium zdalnego:

```bash
git pull origin nazwa-galezi
```

Na przykład, aby zaktualizować główną gałąź:
```bash
git checkout main
git pull origin main
```

## Łączenie branchy (merge)

Aby połączyć swoją gałąź z główną gałęzią:

1. Najpierw przejdź na gałąź docelową (zwykle main):
```bash
git checkout main
```

2. Upewnij się, że masz najnowszą wersję:
```bash
git pull origin main
```

3. Wykonaj operację merge:
```bash
git merge nazwa-twojej-galezi
```

Na przykład:
```bash
git merge feature/login-page
```

4. Wypchnij zmiany do repozytorium zdalnego:
```bash
git push origin main
```

## Rozwiązywanie konfliktów

Podczas łączenia branchy mogą pojawić się konflikty. Git oznaczy pliki z konfliktami, które wyglądają tak:

```
<<<<<<< HEAD
Kod z gałęzi, do której mergujemy
=======
Twój kod z twojej gałęzi
>>>>>>> nazwa-twojej-galezi
```

Aby rozwiązać konflikt:

1. Otwórz plik z konfliktem w edytorze tekstu
2. Edytuj plik, usuwając znaczniki konfliktu i pozostawiając pożądaną wersję kodu
3. Dodaj rozwiązane pliki do kolejki zmian:
```bash
git add sciezka/do/pliku-z-konfliktem.txt
```
4. Zakończ proces merge:
```bash
git commit
```

## Przydatne komendy

- Sprawdzenie historii commitów:
```bash
git log
```

- Przegląd zmian w konkretnym pliku:
```bash
git diff sciezka/do/pliku.txt
```

- Zmiana nazwy gałęzi:
```bash
git branch -m stara-nazwa nowa-nazwa
```

- Usunięcie lokalnej gałęzi:
```bash
git branch -d nazwa-galezi
```

- Cofnięcie ostatniego commita (zachowuje zmiany):
```bash
git reset HEAD~1
```

- Sprawdzenie dostępnych gałęzi:
```bash
git branch
```

- Tymczasowe odłożenie zmian (stash):
```bash
git stash
```

- Przywrócenie odłożonych zmian:
```bash
git stash pop
```

---


