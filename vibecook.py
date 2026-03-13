import streamlit as st
import requests

# --- 1. CONFIG & API KEY ---
API_KEY = "62b81ab8ac634d59b045f0f87cbbab04" 
STAPLES = ["salt", "pepper", "olive oil", "water", "sugar", "flour", "butter", "garlic", "onion"]

# --- 2. HELPER FUNCTIONS ---
def get_time_category(minutes):
    if minutes <= 30: return "⚡ Fast"
    return f"⏰ {minutes}m"

def get_health_vibe(score):
    if score >= 80: return "🟢 High Nutrient"
    if score >= 40: return "🟡 Balanced"
    return "🔴 Indulgent"

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="PantryZero", page_icon="✅", layout="centered")

st.title("✅ PantryZero")
st.markdown("### *Use everything. Waste nothing.*")

# --- FIXED FEATURED RECIPE (COST: 0 POINTS) ---
if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

if not st.session_state.search_clicked:
    st.markdown("---")
    st.markdown("### 🌟 Featured: Mediterranean Chickpea Salad")
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            # Using a static image URL to save API points
            st.image("https://spoonacular.com/recipeImages/637311-312x231.jpg", use_container_width=True)
        with c2:
            st.write("⚡ Fast | 🟢 High Nutrient")
            st.write("A refreshing, budget-friendly classic using pantry staples.")
            st.link_button("View Recipe", "https://spoonacular.com/recipes/mediterranean-chickpea-salad-637311")

st.markdown("---")

# --- INPUT SECTIONS ---
st.subheader("1. What’s in the pantry?")
pantry_input = st.text_input("Ingredients:", placeholder="e.g. avocado, spinach, oats")

st.subheader("2. Prep Time")
time_limit = st.select_slider("How much time do you have?", options=["30 min", "1 hour", "Any"])

st.subheader("3. Preferences")
col_vibe, col_diet = st.columns(2)
with col_vibe:
    flavor_vibe = st.radio("Flavor Profile:", ["Savory 🥘", "Sweet 🍬", "Any ✨"], horizontal=True)
with col_diet:
    diet_pref = st.multiselect(
        "Dietary Restrictions:",
        ["Vegetarian", "Vegan", "Gluten Free", "Dairy Free", "Kosher", "Low Sodium", "Halal"]
    )

st.subheader("4. Health")
health_min = st.slider("Minimum Health Score (0-100):", 0, 100, 0)

# --- 4. THE BUDGET SEARCH LOGIC ---
if st.button("Find Recipes", use_container_width=True):
    st.session_state.search_clicked = True
    if not pantry_input:
        st.error("Please tell us what's in your pantry first!")
    else:
        url = "https://api.spoonacular.com/recipes/complexSearch"
        api_diets = [d for d in diet_pref if d not in ["Low Sodium", "Halal"]]
        
        # BUDGET SETTINGS: Reduced number and removed fillIngredients
        params = {
            "apiKey": API_KEY,
            "includeIngredients": pantry_input,
            "addRecipeInformation": True, 
            "number": 10,           # Lowered from 20 to 10 to save points
            "ranking": 1, 
            "ignorePantry": True,
            "diet": ",".join(api_diets).lower()
        }
        
        if "Low Sodium" in diet_pref:
            params["maxSodium"] = 500
        
        with st.spinner('Scanning the kitchen universe...'):
            try:
                response = requests.get(url, params=params)
                
                # Show points used in the sidebar for transparency
                used_points = response.headers.get('x-api-quota-used', 'Unknown')
                st.sidebar.write(f"📊 Points used today: {used_points}/150")

                data = response.json()

                if "results" in data and len(data["results"]) > 0:
                    found_any = False
                    for recipe in data["results"]:
                        # Filters
                        max_mins = 30 if time_limit == "30 min" else 60 if time_limit == "1 hour" else 1000
                        if recipe['readyInMinutes'] > max_mins: continue
                        if recipe['healthScore'] < health_min: continue
                        
                        # Halal Guardrail
                        if "Halal" in diet_pref:
                            if any(bad in recipe['title'].lower() for bad in ['pork', 'bacon', 'ham', 'wine', 'alcohol']):
                                continue
                        
                        # Flavor Vibe
                        dish_types = recipe.get('dishTypes', [])
                        is_sweet = any(tag in ['dessert', 'pancake', 'sweet', 'cake'] for tag in dish_types)
                        if flavor_vibe == "Sweet 🍬" and not is_sweet: continue
                        if flavor_vibe == "Savory 🥘" and is_sweet: continue

                        found_any = True
                        with st.container(border=True):
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                st.image(recipe['image'], use_container_width=True)
                            with c2:
                                st.markdown(f"### {recipe['title']}")
                                st.write(f"{get_time_category(recipe['readyInMinutes'])} | {get_health_vibe(recipe['healthScore'])}")
                                
                                # Budget-friendly ingredient display
                                miss_count = recipe.get('missedIngredientCount', 0)
                                if miss_count == 0:
                                    st.success("✅ Ready to cook now!")
                                else:
                                    st.info(f"🛒 Missing about {miss_count} ingredients")
                                
                                st.link_button("View Recipe", recipe['sourceUrl'])
                    
                    if not found_any:
                        st.warning("Filters are too strict! Try lowering the Health Score.")
                else:
                    st.warning("No recipes found! (Or API limit reached).")
            except Exception as e:
                st.error(f"Error: {e}")
