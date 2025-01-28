# Recipeasy

Recipeasy is a Django-based web application that helps users manage recipes, shop for ingredients, and schedule their meals. The app includes social authentication via Google, a calendar for recipe scheduling, and clean, responsive design with GSAP animations.

## Features

- **Recipe Management**: Users can add their favorite recipes, view ingredients, and access recipe details.
- **Ingredient Shopping**: Users can shop for ingredients directly from the recipe page.
- **Recipe Scheduling**: Users can schedule recipes on a calendar.
- **Social Authentication**: Login with Google for easy access.
- **Responsive Design**: The app adapts to different screen sizes, making it mobile-friendly.

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Abiram116/Recipeasy.git
```
### 2. Set up the virtual environment
- On Windows:
```bash
.\venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Apply migrations
```bash
python manage.py migrate
```
### 5. Run the development server
```bash
python manage.py runserver
```

## Usage
- Home Page: Displays the introduction to the app, recipes, and GSAP animations.
- Recipe Pages: Users can explore recipes, view ingredients, and add recipes to their list.
- Calendar: Schedule recipes by adding them to the calendar.
- Social Login: Use Google authentication to log in and manage your recipes.

## Technologies Used
- Backend: Django (SQLite)
- Frontend: HTML, CSS, JavaScript (GSAP animations)
- Authentication: Google OAuth 2.0
- Deployment: Render

## Credits
- GSAP: For animations on the home page.
- Google OAuth: For social authentication.

## License
**This project is open-source and available under the MIT License.**
