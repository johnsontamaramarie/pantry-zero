import streamlit as st
import requests
import random

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

# --- FEATURED RECIPE LOGIC ---
if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

if not st.session_state.search_clicked:
    st.markdown("---")
    st.markdown("### 🌟 Featured:")
    st.caption("Healthy, Vegan, Kosher & Halal Friendly")
    
    feat_url = f"https://api.spoonacular.com/recipes/complexSearch"
    feat_params = {
        "apiKey": API_KEY, "diet": "vegan", "minHealthScore": 80, "number": 1, "addRecipeInformation": True
    }
    try:
        f_res = requests.get(feat_url, params=feat_params).json()
        if f_res['results']:
            feat = f_res['results'][0]
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(feat['image'], use_container_width=True)
                with c2:
                    st.markdown(f"#### {feat['title']}")
                    st.write(f"{get_time_category(feat['readyInMinutes'])} | {get_health_vibe(feat['healthScore'])}")
                    st.link_button("Try This Recipe", feat['sourceUrl'])
    except:
        st.write("Welcome! Start by entering your ingredients below.")

st.markdown("---")

# --- INPUT SECTIONS ---
# (1) PANTRY
st.subheader("1. What’s in the pantry?")
pantry_input = st.text_input("Ingredients:", placeholder="e.g. avocado, spinach, oats")

# (2) PREP TIME
st.subheader("2. Prep Time")
time_limit = st.select_slider("How much time do you have?", options=["30 min", "1 hour", "Any"])

# (3) PREFERENCES
st.subheader("3. Preferences")
col_vibe, col_diet = st.columns(2)
with col_vibe:
    flavor_vibe = st.radio("Flavor Profile:", ["Savory 🥘", "Sweet 🍬", "Any ✨"], horizontal=True)
with col_diet:
    diet_pref = st.multiselect(
        "Dietary Restrictions:",
        ["Vegetarian", "Vegan", "Gluten Free", "Dairy Free", "Kosher", "Low Sodium", "Halal"]
    )

# (4) HEALTH
st.subheader("4. Health")
health_min = st.slider("Minimum Health Score (0-100):", 0, 100, 0)

# --- 4. THE SEARCH LOGIC ---
if st.button("Find Recipes", use_container_width=True):
    st.session_state.search_clicked = True
    if not pantry_input:
        st.error("Please tell us what's in your pantry first!")
    else:
        url = "https://api.spoonacular.com/recipes/complexSearch"
        
        # Filter logic
        api_diets = [d for d in diet_pref if d not in ["Low Sodium", "Halal"]]
        
        params = {
            "apiKey": API_KEY,
            "query": pantry_input,
            "addRecipeInformation": True,
            "fillIngredients": True,
            "number": 15,
            "sort": "min-missing-ingredients",
            "diet": ",".join(api_diets).lower()
        }
        
        if "Low Sodium" in diet_pref:
            params["maxSodium"] = 500
        
        with st.spinner('Scanning the fridge...'):
            try:
                response = requests.get(url, params=params)
                data = response.json()

                if "results" in data and len(data["results"]) > 0:
                    for recipe in data["results"]:
                        # Filters
                        max_mins = 30 if time_limit == "30 min" else 60 if time_limit == "1 hour" else 1000
                        if recipe['readyInMinutes'] > max_mins: continue
                        if recipe['healthScore'] < health_min: continue
                        
                        # Halal Guardrail
                        if "Halal" in diet_pref:
                            if any(bad in recipe['title'].lower() for bad in ['pork', 'bacon', 'ham', 'wine', 'alcohol']): continue
                        
                        # Flavor Vibe
                        is_sweet = any(tag in ['dessert', 'pancake', 'sweet', 'cake'] for tag in recipe.get('dishTypes', []))
                        if flavor_vibe == "Sweet 🍬" and not is_sweet: continue
                        if flavor_vibe == "Savory 🥘" and is_sweet: continue

                        with st.container(border=True):
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                st.image(recipe['image'], use_container_width=True)
                            with c2:
                                st.markdown(f"### {recipe['title']}")
                                st.write(f"{get_time_category(recipe['readyInMinutes'])} | {get_health_vibe(recipe['healthScore'])}")
                                
                                real_miss = [i['name'] for i in recipe['missedIngredients'] if i['name'].lower() not in STAPLES]
                                if not real_miss:
                                    st.success("✅ Ready to cook now!")
                                else:
                                    st.info(f"🛒 Missing: {', '.join(real_miss[:2])}")
                                
                                st.link_button("View Recipe", recipe['sourceUrl'])
                else:
                    st.warning("No recipes found! Try broadening your pantry list.")
            except Exception as e:
                st.error(f"Error connecting to the kitchen universe: {e}")
