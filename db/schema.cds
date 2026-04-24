namespace sap.procure;

entity Suppliers {
    key ID : String;
    name   : String;
    contractTerms : String;
    status : String;
}

entity PurchaseOrders {
    key ID : String;
    vendorName : String;
    totalAmount : Decimal(15,2);
    items : String;
    aiRiskScore : Decimal(5,2);
    aiAnalysis  : String;
    status : String(20) default 'PENDING';
}

entity AuditLogs {
    key ID          : UUID;
    po_ID           : String(20);
    action          : String(50); // e.g., 'APPROVED'
    performedAt     : DateTime @cds.on.insert: $now;
    performedBy     : String(50) default 'SystemUser'; 
}