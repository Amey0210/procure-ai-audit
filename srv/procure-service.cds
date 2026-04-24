using { sap.procure as my } from '../db/schema';

service ProcureService {
    entity Suppliers @readonly as projection on my.Suppliers;
    entity PurchaseOrders as projection on my.PurchaseOrders;
}

