const cds = require('@sap/cds');
const axios = require('axios');

module.exports = class ProcureService extends cds.ApplicationService {
    async init() {
        this.on('validatePO', async (req) => {
            const { po_content } = req.data;
            
            // 1. Ask Python/ChromaDB: "Do we have a contract for this?"
            const aiResponse = await axios.post('http://localhost:8000/analyze', {
                text: po_content
            });

            return aiResponse.data;
        });
        await super.init();
    }
}