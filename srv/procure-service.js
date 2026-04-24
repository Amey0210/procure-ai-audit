const cds = require('@sap/cds');
const axios = require('axios');

module.exports = class ProcureService extends cds.ApplicationService {
    async init() {
        const { PurchaseOrders, AuditLogs } = this.entities;

        // --- FEATURE 1: AI Audit with Heuristic Severity Scoring ---
        this.before('CREATE', PurchaseOrders, async (req) => {
            const po = req.data;
            
            po.ID = po.ID || `PO-${Math.floor(Math.random() * 10000)}`;
            po.totalAmount = parseFloat(po.totalAmount) || 0;
            
            const poText = `PO ID: ${po.ID}. Vendor: ${po.vendorName || 'N/A'}. Amount: $${po.totalAmount}. Items: ${po.items || 'N/A'}`;

            console.log(`[SAP-CAP] >> Initiating AI Audit for PO: ${po.ID}`);

            try {
                const response = await axios.post('http://127.0.0.1:8000/analyze-po', {
                    text: poText
                }, { timeout: 10000 });

                const analysisText = response.data.analysis || "No analysis provided.";
                const analysisLower = analysisText.toLowerCase();
                
                // Initialize default state
                let score = 1.0; 
                let reasoning = "";

                // Prioritized Risk Logic
                if (analysisLower.includes("exceeds") || analysisLower.includes("violation") || analysisLower.includes("violates")) {
                    score = 9.0;
                    reasoning = "\n\n[SYSTEM: Critical Policy Violation Detected]";
                } 
                else if (analysisLower.includes("mismatch") || (analysisLower.includes("discount") && analysisLower.includes("recommendation"))) {
                    score = 5.0;
                    reasoning = "\n\n[SYSTEM: Data Quality Flag - Human Review Advised]";
                } 
                else if (analysisLower.includes("potential issue") || analysisLower.includes("observation")) {
                    score = 3.0;
                    reasoning = "\n\n[SYSTEM: Minor Observation - Proceed with Caution]";
                }
                
                po.aiRiskScore = score;
                po.aiAnalysis = (analysisText + reasoning).substring(0, 4000);

            } catch (err) {
                console.error(`[SAP-CAP] !! AI Sidecar Error: ${err.message}`);
                po.aiAnalysis = "Automated Audit temporarily unavailable.";
                po.aiRiskScore = 0.00; 
            }
        });

        // --- FEATURE 3: Automated Audit Logging (After Approval) ---
        this.after('PATCH', 'PurchaseOrders', async (data, req) => {
            if (data.status === 'APPROVED') {
                try {
                    const existingLog = await SELECT.one.from(AuditLogs).where({ po_ID: data.ID, action: 'APPROVED' });
                    if (!existingLog) {
                        await INSERT.into(AuditLogs).entries({
                            po_ID: data.ID,
                            action: 'APPROVED',
                            performedBy: 'ProcurementOfficer' 
                        });
                        console.log(`[SAP-CAP] Audit log entry created for PO: ${data.ID}`);
                    }
                } catch (err) {
                    console.error(`[SAP-CAP] !! Audit Logging Failed: ${err.message}`);
                }
            }
        });

        return super.init();
    }
}