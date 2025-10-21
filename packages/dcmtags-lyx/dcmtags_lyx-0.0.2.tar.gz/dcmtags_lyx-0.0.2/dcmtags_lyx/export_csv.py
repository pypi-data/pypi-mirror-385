import pandas as pd
from pathlib import Path
from .hierarchy_stats import compute_hierarchy_stats

def export_final_csv(all_batches, df_file_list, FOLDER_NAME, DATE_STR, output_dir="./output"):
    # 整理欄位順序並匯出 CSV，檔名包含層級統計
    df_file_list['Dcm_Path'] = df_file_list['Dcm_Path'].astype(str)
    all_batches['Dcm_Path'] = all_batches['Dcm_Path'].astype(str)
    
    # 內部 merge
    all_batches = pd.merge(all_batches, df_file_list, on='Dcm_Path', how='inner')

    # 欄位排序
    columns_to_front = ["PatientID", "AccessionNumber", "StudyInstanceUID",
                        "SeriesInstanceUID", "SOPInstanceUID", "Batch",
                        "Dcm_Path_Series", "Dcm_Path"]
    all_batches = all_batches[columns_to_front + [col for col in all_batches.columns if col not in columns_to_front]]
    
    all_batches_soplist = all_batches[["PatientID", "AccessionNumber", "StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID", "Batch", "Dcm_Path"]]

    # 計算層級統計
    stats = compute_hierarchy_stats(all_batches)

    # 組合檔名
    out_name = f"{FOLDER_NAME}_DcmTags_InstanceLevel_{stats[0]}pid_" \
               f"{stats[2]}st_{stats[3]}se_{stats[5]}ins-{DATE_STR}.csv"
    out_path = Path(output_dir) / out_name

    # 匯出 CSV
    all_batches.to_csv(out_path, index=False)
    print(f"[完成] 已匯出 CSV：{out_path}")
    return out_path
