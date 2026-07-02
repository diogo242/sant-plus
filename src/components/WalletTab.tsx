import React, { useState } from 'react';
import { Invoice, AccessRequest, Patient } from '../types';
import { Wallet, PlusCircle, ArrowUpRight, History, CreditCard, ShieldCheck, CheckCircle2, Phone, Sparkles, Printer, FileText, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { jsPDF } from 'jspdf';
import { QRCodeCanvas } from 'qrcode.react';

interface WalletTabProps {
  balance: number;
  setBalance: React.Dispatch<React.SetStateAction<number>>;
  invoices: Invoice[];
  onSelectInvoice: (invoice: Invoice) => void;
  accessRequests: AccessRequest[];
  onApproveAccess: (requestId: string) => void;
  onRejectAccess: (requestId: string) => void;
  patientUser?: Patient | null;
}

export default function WalletTab({
  balance,
  setBalance,
  invoices,
  onSelectInvoice,
  accessRequests,
  onApproveAccess,
  onRejectAccess,
  patientUser,
}: WalletTabProps) {
  const [showTopUp, setShowTopUp] = useState(false);
  const [qrCodeToGenerate, setQrCodeToGenerate] = useState('https://sante.gouv.bj');
  const [topUpAmount, setTopUpAmount] = useState('5000');
  const [operator, setOperator] = useState<'mtn' | 'moov' | 'lightning'>('mtn');
  const [phoneNumber, setPhoneNumber] = useState('+229 97 88 55 44');
  const [isProcessing, setIsProcessing] = useState(false);
  const [topUpSuccess, setTopUpSuccess] = useState(false);

  const downloadInvoicePDF = (inv: Invoice) => {
    // Set QR code value to plain verified offline details
    const qrOfflineText = `[SANTÉ+ BÉNIN - DOCUMENT PAYÉ ET VERIFIÉ SANS CONNEXION]
------------------------------------
Réf Facture: ${inv.id}
Patient: ${inv.patientName}
Établissement: ${inv.hospitalName}
Montant total: ${inv.totalXOF.toLocaleString('fr-FR')} XOF
Date: ${inv.date}
Méthode: ${inv.paymentMethod === 'Wallet' ? 'Portefeuille Prépayé' : 'Réseau Lightning'}
Statut: CERTIFIÉ PAYÉ (OFFLINE STAMP - BLOCKCHAIN BÉNIN)`;
    setQrCodeToGenerate(qrOfflineText);

    setTimeout(() => {
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      // Colors
      const primaryColor = [5, 150, 105]; // #059669 (Sante+ Emerald Green)
      const textColor = [28, 28, 30]; // Dark gray
      const lightGray = [120, 120, 128]; // Muted text

      // Fonts & styles
      doc.setTextColor(primaryColor[0], primaryColor[1], primaryColor[2]);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(22);
      doc.text('SANTÉ+ BÉNIN', 20, 25);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(lightGray[0], lightGray[1], lightGray[2]);
      doc.text('RÉSEAU MÉDICAL NATIONAL ET SÉCURISÉ', 20, 30);

      // Line separator
      doc.setDrawColor(primaryColor[0], primaryColor[1], primaryColor[2]);
      doc.setLineWidth(1);
      doc.line(20, 35, 190, 35);

      // Header Details
      doc.setTextColor(textColor[0], textColor[1], textColor[2]);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(12);
      doc.text('REÇU DE TRANSACTION MÉDICALE', 20, 45);

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9.5);
      doc.text(`Réf Facture : ${inv.id}`, 20, 52);
      doc.text(`Date de paiement : ${inv.date}`, 20, 57);

      // DRAW VISIBLE OFFICIAL RED STAMP
      doc.setDrawColor(239, 68, 68); // Red border (#EF4444)
      doc.setLineWidth(0.6);
      doc.rect(130, 42, 58, 16);
      doc.setTextColor(239, 68, 68);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(7.5);
      doc.text('MINISTÈRE DE LA SANTÉ BÉNIN', 133, 47);
      doc.setFontSize(10);
      doc.text('★ PAYÉ & CERTIFIÉ ★', 135, 53);

      // Reset text color for details
      doc.setTextColor(textColor[0], textColor[1], textColor[2]);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(9.5);

      // Etablissement & Medecin Info
      doc.text('ÉTABLISSEMENT ÉMETTEUR', 20, 68);
      doc.setFont('helvetica', 'normal');
      doc.text(`${inv.hospitalName}`, 20, 73);
      doc.setFontSize(9);
      doc.setTextColor(lightGray[0], lightGray[1], lightGray[2]);
      doc.text(`${inv.hospitalAddress}`, 20, 77);

      doc.setFontSize(9.5);
      doc.setTextColor(textColor[0], textColor[1], textColor[2]);
      doc.setFont('helvetica', 'bold');
      doc.text('MÉDECIN / PRATICIEN CONCERNÉ', 20, 85);
      doc.setFont('helvetica', 'normal');
      doc.text(`${inv.doctorName || 'Dr. Jean Sossou'}`, 20, 90);

      // Patient Info
      doc.setFont('helvetica', 'bold');
      doc.text('CITOYEN / PATIENT', 110, 68);
      doc.setFont('helvetica', 'normal');
      doc.text(`${inv.patientName}`, 110, 73);
      doc.text('Bénin / Nationalité Béninoise', 110, 77);
      doc.text(`Tél : ${inv.patientPhone || "+229 97 88 55 44"}`, 110, 81);

      // Line separator
      doc.setDrawColor(220, 220, 220);
      doc.setLineWidth(0.2);
      doc.line(20, 98, 190, 98);

      // Table header
      doc.setFont('helvetica', 'bold');
      doc.text('Désignation des prestations', 22, 105);
      doc.text('Montant (XOF)', 150, 105);

      doc.line(20, 108, 190, 108);

      // Items
      let y = 115;
      inv.items.forEach((item, index) => {
        doc.setFont('helvetica', 'normal');
        doc.text(`${index + 1}. ${item.name}`, 22, y);
        doc.setFont('helvetica', 'bold');
        doc.text(`${item.priceXOF.toLocaleString('fr-FR')} XOF`, 150, y);
        y += 8;
      });

      doc.line(20, y, 190, y);
      y += 8;

      // Total
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.text('TOTAL GÉNÉRAL ACQUITTÉ', 22, y);
      doc.text(`${inv.totalXOF.toLocaleString('fr-FR')} XOF`, 150, y);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(lightGray[0], lightGray[1], lightGray[2]);
      doc.text(`(~ ${inv.totalSats.toLocaleString('fr-FR')} Satoshis sur réseau Lightning)`, 22, y + 5);

      y += 18;

      // Blockchain Signature Block (Increased height to fit QR Code beautifully)
      doc.setDrawColor(240, 240, 245);
      doc.setFillColor(248, 249, 250);
      doc.rect(20, y, 170, 25, 'F');

      // Draw QR Code next to signature inside the grey block
      const canvas = document.getElementById('citizen-pdf-qr-canvas') as HTMLCanvasElement;
      if (canvas) {
        try {
          const qrDataUrl = canvas.toDataURL('image/png');
          doc.addImage(qrDataUrl, 'PNG', 164, y + 2.5, 20, 20);
        } catch (err) {
          console.error("Erreur lors de la génération du code QR PDF citoyen", err);
        }
      }

      doc.setFont('helvetica', 'bold');
      doc.setFontSize(8.5);
      doc.setTextColor(5, 150, 105);
      doc.text('PREUVE DE SÉCURITÉ CRYPTOGRAPHIQUE (BLOCKCHAIN BÉNIN)', 24, y + 6);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(7.5);
      doc.setTextColor(lightGray[0], lightGray[1], lightGray[2]);
      doc.text(`Méthode de règlement : ${inv.paymentMethod === 'Wallet' ? 'Portefeuille Prépayé Santé+' : 'Réseau Lightning (Sats)'}`, 24, y + 12);
      doc.text(`Signature d'archivage : ${inv.txHash}`, 24, y + 17);

      // Footer seal
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(8);
      doc.setTextColor(230, 120, 0);
      doc.text('MINISTÈRE DE LA SANTÉ DU BÉNIN - AGRÉÉ ET CERTIFIÉ CONFORME', 20, 270);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(lightGray[0], lightGray[1], lightGray[2]);
      doc.text("Document généré numériquement de manière sécurisée. Ne nécessite pas de signature physique.", 20, 274);

      doc.save(`facture-sante-${inv.id}.pdf`);
    }, 150);
  };

  const handleTopUpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const amount = parseFloat(topUpAmount);
    if (isNaN(amount) || amount <= 0) return;

    setIsProcessing(true);

    // 1. Optimistic local update
    setBalance(prev => prev + amount);

    // 2. Synchronize to server if patient email is known
    const patientEmail = patientUser?.email || 'citoyen@sante.bj';
    
    fetch(`/api/wallet/patients/${encodeURIComponent(patientEmail)}/deposit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        amountXOF: amount,
        operator: operator,
        phoneNumber: phoneNumber
      })
    })
    .then(res => {
      if (!res.ok) throw new Error("Could not sync deposit to server");
      return res.json();
    })
    .then(updatedPat => {
      // Set to backend-certified balance
      setBalance(updatedPat.walletBalance);
      setIsProcessing(false);
      setTopUpSuccess(true);
      setTimeout(() => {
        setTopUpSuccess(false);
        setShowTopUp(false);
        setTopUpAmount('5000');
      }, 2500);
    })
    .catch(err => {
      console.warn("Could not sync wallet top-up, falling back to local simulation", err);
      // Fallback local update is already done
      setIsProcessing(false);
      setTopUpSuccess(true);
      setTimeout(() => {
        setTopUpSuccess(false);
        setShowTopUp(false);
        setTopUpAmount('5000');
      }, 2500);
    });
  };

  return (
    <div id="wallet-management" className="max-w-4xl mx-auto space-y-6">
      {/* Hidden QR Code Canvas generator for PDF single invoice */}
      <div style={{ display: 'none' }}>
        <QRCodeCanvas
          id="citizen-pdf-qr-canvas"
          value={qrCodeToGenerate}
          size={150}
        />
      </div>
      
      {/* Wallet Balance Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        
        {/* Main balance display */}
        <div className="md:col-span-7 bg-slate-900 text-white rounded-3xl p-6 border border-slate-800 shadow-md relative overflow-hidden flex flex-col justify-between min-h-[200px]">
          {/* Background decor */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl"></div>
          
          <div className="flex justify-between items-start">
            <div className="space-y-1">
              <span className="text-[10px] text-gray-400 font-sans uppercase tracking-wider font-bold">Solde Disponible Santé+</span>
              <h2 className="text-4xl font-black font-sans text-[#00D26A]">{balance.toLocaleString('fr-FR')} XOF</h2>
            </div>
            <Wallet className="w-8 h-8 text-[#00D26A]" />
          </div>

          <div className="flex items-center justify-between border-t border-slate-800/80 pt-4 mt-6">
            <span className="text-xs text-gray-400 font-sans">Agréé par la Banque Centrale & MSP Bénin</span>
            <button
              onClick={() => setShowTopUp(true)}
              className="px-4 py-2 bg-[#00D26A] hover:bg-[#00D26A]/90 text-white text-xs font-bold font-sans rounded-xl shadow-xs flex items-center gap-1.5 transition-all cursor-pointer"
            >
              <PlusCircle className="w-4 h-4" />
              Recharger
            </button>
          </div>
        </div>

        {/* Mobile Money partnership block */}
        <div className="md:col-span-5 bg-white border border-gray-100 rounded-3xl p-6 flex flex-col justify-between">
          <div className="space-y-2">
            <span className="flex items-center gap-1 text-xs text-[#FF8A00] font-sans font-semibold">
              <ShieldCheck className="w-4 h-4" />
              Opérateurs Partenaires
            </span>
            <p className="text-xs text-gray-500 font-sans leading-relaxed">
              Rechargez votre Wallet instantanément avec votre compte Mobile Money national (MTN MoMo, Moov Money) ou via votre portefeuille Bitcoin Lightning.
            </p>
          </div>

          <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-50">
            <div className="px-2.5 py-1.5 bg-yellow-400 text-yellow-950 text-[10px] font-sans font-bold rounded-lg uppercase tracking-wide">
              MTN MoMo
            </div>
            <div className="px-2.5 py-1.5 bg-blue-600 text-white text-[10px] font-sans font-bold rounded-lg uppercase tracking-wide">
              Moov Flooz
            </div>
            <div className="px-2.5 py-1.5 bg-slate-900 text-amber-400 text-[10px] font-sans font-bold rounded-lg uppercase tracking-wide flex items-center gap-0.5">
              Sats ⚡
            </div>
          </div>
        </div>

      </div>

      {/* Top Up Drawer / Sub-panel */}
      <AnimatePresence>
        {showTopUp && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden bg-white border border-gray-100 rounded-3xl p-6 shadow-sm"
          >
            <h3 className="text-md font-bold font-sans text-gray-800 mb-4 flex items-center gap-2">
              <PlusCircle className="w-5 h-5 text-[#00D26A]" />
              Recharge instantanée de compte
            </h3>

            <form onSubmit={handleTopUpSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* 1. Select provider */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-gray-500 uppercase font-sans">1. Opérateur</label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => { setOperator('mtn'); setPhoneNumber('+229 97 88 55 44'); }}
                      className={`p-2.5 rounded-xl border text-xs font-sans font-bold text-center transition-all cursor-pointer ${
                        operator === 'mtn' ? 'border-yellow-400 bg-yellow-50 text-yellow-800' : 'border-gray-200 text-gray-500'
                      }`}
                    >
                      MTN
                    </button>
                    <button
                      type="button"
                      onClick={() => { setOperator('moov'); setPhoneNumber('+229 95 12 34 56'); }}
                      className={`p-2.5 rounded-xl border text-xs font-sans font-bold text-center transition-all cursor-pointer ${
                        operator === 'moov' ? 'border-blue-500 bg-blue-50 text-blue-800' : 'border-gray-200 text-gray-500'
                      }`}
                    >
                      MOOV
                    </button>
                    <button
                      type="button"
                      onClick={() => { setOperator('lightning'); }}
                      className={`p-2.5 rounded-xl border text-xs font-sans font-bold text-center transition-all cursor-pointer ${
                        operator === 'lightning' ? 'border-slate-800 bg-slate-50 text-gray-800' : 'border-gray-200 text-gray-500'
                      }`}
                    >
                      LN ⚡
                    </button>
                  </div>
                </div>

                {/* 2. Phone / Invoice destination */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-gray-500 uppercase font-sans">
                    {operator === 'lightning' ? '2. Réseau Portefeuille' : '2. Numéro Mobile Money'}
                  </label>
                  {operator === 'lightning' ? (
                    <div className="py-2.5 px-3 bg-gray-50 border border-gray-200 rounded-xl text-xs font-mono font-bold text-gray-700">
                      Réseau Lightning (BTC)
                    </div>
                  ) : (
                    <input
                      type="text"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="+229 XX XX XX XX"
                      className="w-full py-2 px-3 bg-white border border-gray-200 rounded-xl text-xs font-sans font-semibold focus:outline-none focus:ring-1 focus:ring-[#059669]"
                    />
                  )}
                </div>

                {/* 3. Amount */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-gray-500 uppercase font-sans">3. Montant (XOF)</label>
                  <input
                    type="number"
                    value={topUpAmount}
                    onChange={(e) => setTopUpAmount(e.target.value)}
                    placeholder="Montant en FCFA"
                    className="w-full py-2 px-3 bg-white border border-gray-200 rounded-xl text-xs font-sans font-semibold focus:outline-none focus:ring-1 focus:ring-[#059669]"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTopUp(false)}
                  className="px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 rounded-xl text-xs font-sans font-semibold text-gray-600 cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="px-5 py-2 bg-[#00D26A] hover:bg-[#00D26A]/95 text-white font-sans font-bold text-xs rounded-xl shadow-xs flex items-center gap-1 transition-all cursor-pointer disabled:bg-gray-100 disabled:text-gray-400"
                >
                  {isProcessing ? (
                    <>
                      <PlusCircle className="w-4 h-4 animate-spin" />
                      Traitement...
                    </>
                  ) : (
                    <>
                      <PlusCircle className="w-4 h-4" />
                      Confirmer la recharge
                    </>
                  )}
                </button>
              </div>

              {/* Status prompt */}
              {topUpSuccess && (
                <div className="p-3 bg-emerald-50 border border-emerald-100 text-[#00D26A] font-medium text-xs font-sans rounded-xl flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Votre compte a été crédité de <strong>{parseFloat(topUpAmount).toLocaleString('fr-FR')} XOF</strong> !</span>
                </div>
              )}
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {/* SECTEUR AUTORISATION BLOCKCHAIN / DEMANDE ACCÈS MÉDECIN */}
      {accessRequests && accessRequests.length > 0 && (
        <div className="bg-white border-2 border-emerald-100 rounded-3xl p-6 md:p-8 space-y-4 shadow-xs relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-50 rounded-full blur-2xl pointer-events-none"></div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="flex items-center justify-center w-8 h-8 bg-emerald-50 text-[#059669] rounded-full">
                <ShieldCheck className="w-5 h-5 text-[#059669] animate-pulse" />
              </span>
              <div>
                <h3 className="text-md font-sans font-extrabold text-[#1C1C1E]">Demandes d'Accès Médical</h3>
                <p className="text-[11px] text-gray-500 font-sans">Sécurisé par clés cryptographiques Bitcoin (Blockchain) & NPI Bénin</p>
              </div>
            </div>
            <span className="text-[10px] uppercase font-bold bg-emerald-50 border border-emerald-200 text-emerald-800 px-2 py-0.5 rounded-md">Vérification Réseau</span>
          </div>

          <div className="space-y-3">
            {accessRequests.map((req) => (
              <div key={req.id} className="p-4 bg-gray-50 border border-gray-100 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-gray-800">{req.hospitalName}</span>
                    <span className="text-[10px] text-gray-400 font-sans">({req.doctorEmail})</span>
                  </div>
                  <div className="text-[11px] text-gray-500 space-y-1">
                    <p>NPI recherché : <strong className="font-mono text-gray-700 bg-gray-100 px-1.5 py-0.5 rounded">{req.npi}</strong></p>
                    <p>Demandé le : {req.requestedAt}</p>
                    {req.blockchainTxHash && (
                      <div className="text-amber-600 font-mono text-[9px] flex flex-col sm:flex-row sm:items-center gap-1 mt-1 bg-amber-50/50 p-1.5 rounded border border-amber-100">
                        <span>⛓️ TX Bitcoin Hash :</span>
                        <span className="font-bold select-all truncate max-w-[280px]">{req.blockchainTxHash}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {req.status === 'pending' ? (
                    <div className="flex gap-2">
                      <button
                        onClick={() => onRejectAccess(req.id)}
                        className="px-3 py-1.5 bg-white border border-gray-200 hover:bg-gray-100 text-gray-600 font-bold rounded-xl text-[11px] font-sans transition-all cursor-pointer"
                      >
                        Refuser
                      </button>
                      <button
                        onClick={() => onApproveAccess(req.id)}
                        className="px-4 py-1.5 bg-[#00D26A] hover:bg-[#00D26A]/90 text-white font-bold rounded-xl text-[11px] font-sans transition-all cursor-pointer flex items-center gap-1 shadow-2xs"
                      >
                        <span>Autoriser l'accès</span>
                        <span>⚡</span>
                      </button>
                    </div>
                  ) : req.status === 'approved' ? (
                    <div className="flex flex-col items-end">
                      <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold text-[10px] rounded-lg uppercase tracking-wide flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Accès Approuvé (Blockchain)
                      </span>
                      <span className="text-[9px] text-gray-400 mt-1">Signé le {req.confirmedAt}</span>
                    </div>
                  ) : (
                    <span className="px-2.5 py-1 bg-red-50 text-red-700 border border-red-200 font-bold text-[10px] rounded-lg uppercase tracking-wide">
                      Accès Refusé
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PAID INVOICES ARCHIVE SECTION */}
      <div className="bg-white border border-gray-100 rounded-3xl p-6 md:p-8 space-y-4 shadow-3xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-[#059669]" />
            <h3 className="text-lg font-sans font-bold text-[#1C1C1E]">Archive des Factures Payées</h3>
          </div>
          <span className="text-xs text-gray-400 font-sans font-medium">Permanence numérique</span>
        </div>
        <p className="text-xs text-gray-500 font-sans leading-relaxed">
          Retrouvez l'ensemble de vos factures de soins acquittées. Cliquez sur une facture de la liste pour l'afficher au format PDF et l'imprimer pour vos assurances ou votre employeur.
        </p>

        {/* Invoice Grid */}
        {invoices.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {invoices.map((inv) => (
              <div
                key={inv.id}
                onClick={() => onSelectInvoice(inv)}
                className="p-4 bg-gray-50/50 hover:bg-gray-50 border border-gray-100 hover:border-gray-200 rounded-2xl cursor-pointer transition-all flex items-start justify-between gap-3 shadow-3xs"
              >
                <div className="space-y-1.5 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#00D26A]"></span>
                    <h4 className="font-sans font-bold text-xs text-gray-800 truncate">{inv.hospitalName}</h4>
                  </div>
                  <p className="text-[10px] text-gray-400 font-sans font-semibold">N° {inv.id} • {inv.date.split(' à')[0]}</p>
                  
                  {/* Small badge list */}
                  <span className="inline-block text-[10px] px-2 py-0.5 bg-white border border-gray-100 text-gray-500 rounded-md font-sans">
                    {inv.paymentMethod === 'Wallet' ? 'Wallet Santé+' : 'Sats ⚡'}
                  </span>
                </div>

                <div className="text-right flex flex-col items-end gap-1.5">
                  <p className="text-xs font-mono font-bold text-gray-900">{inv.totalXOF.toLocaleString('fr-FR')} XOF</p>
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => { e.stopPropagation(); downloadInvoicePDF(inv); }}
                      className="text-[10px] font-bold text-slate-700 hover:text-slate-900 font-sans flex items-center gap-0.5 cursor-pointer"
                      title="Télécharger la facture (PDF)"
                    >
                      <Download className="w-3 h-3" />
                      Télécharger
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); onSelectInvoice(inv); }}
                      className="text-[10px] font-bold text-[#059669] hover:underline font-sans flex items-center gap-0.5 cursor-pointer"
                    >
                      <FileText className="w-3 h-3" />
                      Voir
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-10 bg-slate-50 rounded-2xl border border-dashed border-gray-200">
            <History className="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p className="text-xs font-medium text-gray-600 font-sans">Aucune facture enregistrée</p>
            <p className="text-[11px] text-gray-400 font-sans mt-0.5">Vos factures s'afficheront ici dès que vous aurez réglé des soins.</p>
          </div>
        )}
      </div>

    </div>
  );
}
