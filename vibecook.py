# --- 3. UI LAYOUT ---
st.set_page_config(page_title="PantryZero", page_icon="🥦", layout="centered")

st.title("🥦 PantryZero")
st.markdown("### *Use everything. Waste nothing.*")

# --- FIXED FEATURED RECIPE ---
if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False

if not st.session_state.search_clicked:
    st.markdown("---")
    st.markdown("### 🥦 Featured: Mediterranean Chickpea Salad")
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image("https://spoonacular.com/recipeImages/637311-312x231.jpg", use_container_width=True)
        with c2:
            st.write("⚡ Fast | 🟢 High Nutrient")
            st.write("A refreshing, budget-friendly classic using pantry staples.")
            st.link_button("Open Recipe", "https://spoonacular.com/recipes/mediterranean-chickpea-salad-637311")
