import pandas as pd
import os
from django.conf import settings

def export_classe_excel(classe, data):

    output_dir = os.path.join(settings.BASE_DIR, "media")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"classe_{classe.id}.xlsx")

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

    return file_path