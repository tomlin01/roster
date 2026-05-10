本次啟用：5 個 role-agents（產品拆解、中醫內容、使用者體驗、專業工作流、資料風險；單一回覆中分工處理）  
目前階段：初步規劃；正式 artifact 這輪先不產出。

**核心判斷**

這個 APP 先不要定位成「診斷或治療建議工具」，而要先定位成：

> 體質問卷填答、結果理解、專業端追蹤輔助工具。

MVP 成功標準可以很清楚：一般使用者能完成填答、理解自己的體質傾向與下一步；專業端能看到分數、題目明細、歷次變化、需要追蹤的線索，但不讓系統直接替代專業判斷。

**建議拆法**

1. **量表與分數規則先定版**
   先確認用哪一份中醫體質問卷、題目文字、授權/IP、分數算法、體質分類門檻、混合體質怎麼判、是否有版本差異。這是最底層，不能邊做邊猜。

2. **一般使用者端**
   流程是：同意與用途說明 -> 填答 -> 送出 -> 顯示體質傾向 -> 給安全的生活建議或就診提醒。  
   文字要保守，用「傾向」「可能」「建議諮詢專業人員」，不要寫成確診。

3. **專業端**
   流程是：個案列表 -> 單次結果 -> 分數組成 -> 題目明細 -> 歷次追蹤 -> 備註/待追蹤事項。  
   專業端重點不是漂亮結果頁，而是可追蹤、可解釋、可回看。

4. **共用後端**
   只做一套 scoring engine。使用者端和專業端讀同一份分數快照，但顯示不同層級的資訊。這可以避免兩端算出不同結果。

5. **驗證與試跑**
   先做小型測試：幾位一般使用者填答、幾位專業者看結果，確認題目理解、分數正確、結果不誤導、專業端真的能幫助後續追蹤。

**先處理的風險**

優先順序我會排成這樣：

1. **用途與法規邊界**
   如果只是健康生活與自我理解，風險較低；如果開始說「診斷」「治療」「處方」「疾病風險判斷」，就會進入更高風險區。美國 FDA 對 device software 是依功能與風險看待；一般 wellness 類產品若只是維持健康生活、且不涉及疾病診斷治療，通常是另一條線。若專業端開始提供臨床決策建議，還要看 CDS 邊界。參考：FDA device software、general wellness、CDS guidance。

2. **問卷有效性與授權**
   量表來源、授權、適用族群、中文版本、分數門檻都要先釐清。這比 UI 更重要。

3. **安全措辭**
   一般端不能讓使用者以為「我已被診斷為某體質」。專業端也不能讓分數看起來像自動醫囑。

4. **健康資料與權限**
   問卷答案、體質結果、追蹤紀錄都可能是敏感健康資料。需要同意、角色權限、加密、查閱紀錄、刪除/匯出策略。若在美國市場且與診所/醫療機構合作，還要判斷 HIPAA covered entity / business associate 關係；若是消費者健康資料，也要注意 FTC health breach notification 規則。台灣情境則至少要按健康/醫療資料保護邏輯設計權限與紀錄。

5. **兩端互相干擾**
   一般端重點是理解與安心；專業端重點是明細與判斷。兩端不能共用同一套文案和資訊密度。

**避免兩端打架的設計原則**

最重要的是「同資料、不同視圖、不同權限」。

- 使用者端可以：建立填答、送出前修改、看自己的結果、同意分享給專業端。
- 專業端可以：看已授權個案、看分數與題目明細、加註追蹤紀錄、標記待追蹤線索。
- 專業端不應該：改使用者原始答案、覆寫原始分數。
- 系統管理端可以：發布新版問卷與算法。
- 系統管理端不應該：讓新版算法偷偷改掉舊紀錄；舊紀錄要保留當時的問卷版本與分數快照。

建議資料狀態：

`草稿 -> 已送出 -> 已計分 -> 已分享給專業端 -> 已審閱 -> 已安排追蹤 -> 封存`

建議資料核心：

`AssessmentSnapshot`：一次填答的不可變快照  
`ScoreResult`：分數與分類結果  
`ConsumerResultView`：一般端呈現  
`ProfessionalReviewView`：專業端呈現  
`FollowUpCue`：追蹤線索，不是自動治療建議  
`ProfessionalNote`：專業者備註，與原始答案分開存

**參考線索**

我有用官方來源快速校準風險邊界：FDA 對 device software / mobile medical apps 採功能與風險導向；general wellness guidance 目前標示為 2026 年 1 月版本；CDS guidance 也更新到 2026 年 1 月頁面。HHS 說 HIPAA 主要適用 covered entities / business associates；FTC Health Breach Notification Rule 則涵蓋某些非 HIPAA 健康資料 breach 通知情境。台灣衛福部 EMR/FHIR 指引也明確強調授權、角色控管、加密、監控與日誌。

來源：  
FDA Device Software Functions: https://www.fda.gov/medical-devices/digital-health-center-excellence/device-software-functions-including-mobile-medical-applications  
FDA General Wellness: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/general-wellness-policy-low-risk-devices  
FDA CDS: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software  
HHS HIPAA covered entities: https://www.hhs.gov/hipaa/for-professionals/covered-entities/index.html  
FTC Health Breach Notification Rule: https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule  
台灣 EMR-IG 安全性: https://twcore.mohw.gov.tw/ig/emr/Security.html

**本次分工執行**

- 產品拆解：把任務拆成一般端、專業端、共用後端、驗證四塊。
- 中醫內容視角：把量表來源、分數規則、適用族群列為前置風險。
- 使用者體驗視角：要求一般端降低誤解與焦慮，不用診斷式文案。
- 專業工作流視角：保留分數、題目明細、追蹤線索與備註，但不覆寫原始填答。
- 資料風險視角：用角色權限、快照、版本化與稽核紀錄避免兩端衝突。

**最後收斂**

下一步不是直接寫 PRD，而是先產一份「需求拆解草案」或「低保真原型規格」：確認量表、角色、資料狀態、兩端頁面、法規/安全邊界。  
下一句可以直接說：`Roster，把這個整理成低保真原型規格，但先不要寫正式 PRD。`

