import tempfile
from pathlib import Path
import streamlit as st

import greedy_rando

st.title("Greedy Rando")

user_pref_file = st.file_uploader("User preferences CSV", type="csv")
session_cap_file = st.file_uploader("Session capacities CSV", type="csv")
n_iter = st.number_input("Iterations (n_iter)", min_value=1, value=1000, step=1)

if st.button("Run assignments"):
    if not user_pref_file or not session_cap_file:
        st.warning("Upload both CSV files before running.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            user_pref_path = tmpdir_path / "user_pref.csv"
            session_cap_path = tmpdir_path / "session_cap.csv"

            user_pref_path.write_bytes(user_pref_file.getvalue())
            session_cap_path.write_bytes(session_cap_file.getvalue())

            try:
                greedy_rando.main(
                    [
                        str(user_pref_path),
                        str(session_cap_path),
                        "--n-iter",
                        str(int(n_iter)),
                    ]
                )
            except ValueError as exc:
                st.error(f"Error while assigning sessions: {exc}")
                st.stop()

        best_path = Path("best_assignments.csv")
        if best_path.exists():
            st.success("Assignments complete.")
            st.download_button(
                "Download best_assignments.csv",
                data=best_path.read_bytes(),
                file_name="best_assignments.csv",
                mime="text/csv",
            )
        else:
            st.error("No output file found.")
