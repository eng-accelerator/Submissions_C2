"""
Price Comparison UI Component for Streamlit
Provides interface for comparing product prices across websites
"""

import streamlit as st
from price_comparison import compare_prices


def render_price_comparison_tab():
    """Render the price comparison interface in Streamlit"""

    st.markdown("### 💰 Product Price Comparison")
    st.markdown("Compare product prices across multiple e-commerce websites to find the best deals.")

    # Input section
    col1, col2 = st.columns([3, 1])

    with col1:
        product_name = st.text_input(
            "Product Name",
            placeholder="e.g., iPhone 15 Pro, Sony WH-1000XM5, Nike Air Max...",
            key="price_product_input"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Search Prices", type="primary", use_container_width=True)

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        custom_websites = st.text_area(
            "Custom Websites (one per line, optional)",
            placeholder="https://www.amazon.com\nhttps://www.ebay.com\nhttps://www.walmart.com",
            height=100
        )
        max_websites = st.slider("Maximum websites to check", 2, 10, 4)

    st.markdown("---")

    # Results section
    if search_button:
        if not product_name.strip():
            st.error("⚠️ Please enter a product name")
        else:
            # Parse custom websites if provided
            websites = None
            if custom_websites.strip():
                websites = [url.strip() for url in custom_websites.split('\n') if url.strip()]
                websites = websites[:max_websites]

            with st.spinner(f"🔍 Searching for '{product_name}' across multiple websites..."):
                comparison_result = compare_prices(product_name, websites)

            # Display summary
            st.markdown("### 📊 Results")

            if comparison_result.get('best_deal'):
                best = comparison_result['best_deal']

                # Highlight best deal
                st.success(f"""
                **🏆 Best Deal Found!**

                **Product:** {product_name}
                **Price:** {best['price']}
                **Website:** {best['website']}
                """)

                if best.get('link'):
                    st.markdown(f"[🔗 View Product on {best['website']}]({best['link']})")

                st.markdown("---")

            # Summary info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Websites Checked", comparison_result['total_checked'])
            with col2:
                st.metric("Prices Found", comparison_result['successful'])
            with col3:
                if comparison_result.get('best_deal'):
                    savings = "Check prices!"
                    st.metric("Status", "✅ Success")
                else:
                    st.metric("Status", "⚠️ Limited")

            # Detailed results
            st.markdown("### 📋 Detailed Results")

            results = comparison_result.get('results', [])

            if results:
                # Successful results
                successful = [r for r in results if r.get('status') == 'success' and r.get('price')]

                if successful:
                    st.markdown("**✅ Prices Found:**")
                    # Sort by price
                    successful_sorted = sorted(successful, key=lambda x: x.get('price_numeric', float('inf')))

                    for result in successful_sorted:
                        col1, col2, col3 = st.columns([2, 1, 1])

                        with col1:
                            st.markdown(f"**{result['website']}**")
                        with col2:
                            st.markdown(f"`{result['price']}`")
                        with col3:
                            if result.get('link'):
                                st.markdown(f"[🔗 View]({result['link']})")

                # Failed results
                failed = [r for r in results if r.get('status') != 'success' or not r.get('price')]

                if failed:
                    with st.expander(f"⚠️ Could not retrieve prices from {len(failed)} website(s)"):
                        for result in failed:
                            st.markdown(f"- **{result['website']}**: {result.get('error', 'Price not found')}")
            else:
                st.warning("No results found. The product might not be available or websites couldn't be accessed.")

            # Display full summary
            st.markdown("---")
            st.markdown("### 📝 Summary")
            st.markdown(comparison_result.get('summary', ''))

    # Example products
    with st.expander("💡 Example Products to Search"):
        st.markdown("""
        **Electronics:**
        - iPhone 15 Pro
        - Samsung Galaxy S24
        - Sony WH-1000XM5 headphones
        - Apple Watch Series 9

        **Gaming:**
        - PlayStation 5
        - Xbox Series X
        - Nintendo Switch OLED

        **Other:**
        - Nike Air Max 90
        - Dyson V15 vacuum
        - Instant Pot Duo
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Search iPhone 15 Pro", key="ex1"):
                st.session_state["price_product_input"] = "iPhone 15 Pro"
                st.rerun()

        with col2:
            if st.button("Search PS5", key="ex2"):
                st.session_state["price_product_input"] = "PlayStation 5"
                st.rerun()

        with col3:
            if st.button("Search AirPods Pro", key="ex3"):
                st.session_state["price_product_input"] = "Apple AirPods Pro"
                st.rerun()

    # Disclaimer
    st.markdown("---")
    st.info("""
    **ℹ️ Disclaimer:** Prices are scraped from public websites and may not always be accurate or up-to-date.
    Please verify prices on the actual website before making a purchase.
    """)
