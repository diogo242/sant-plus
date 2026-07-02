import React, { useState, useEffect } from 'react';
import { Patient, MedicalConsultation } from '../types';
import { UserPlus, Stethoscope, ShieldCheck, Lock, Eye, CheckCircle2, Bitcoin, QrCode, ArrowRight, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { QRCodeSVG } from 'qrcode.react';

type Role = 'none' | 'patient' | 'agent';
type Step = 'create' | 'patient_view' | 'agent_confirm' | 'patient_see_update' | 'bitcoin_pay' | 'done';

async function generateSHA256(data: string): Promise<string> {
  const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(data));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function aesEncrypt(text: string, keyHex: string): Promise<{ iv: string; ciphertext: string }> {
  const keyBytes = new Uint8Array(keyHex.match(/.{2}/g)!.map((byte) => parseInt(byte, 16)));
  const key = await crypto.subtle.importKey('raw', keyBytes, { name: 'AES-GCM' }, false, ['encrypt']);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, new TextEncoder().encode(text));
  return {
    iv: Array.from(iv).map((b) => b.toString(16).padStart(2, '0')).join(''),
    ciphertext: Array.from(new Uint8Array(encrypted)).map((b) => b.toString(16).padStart(2, '0')).join(''),
  };
}

function randomTxHash() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return '0x' + Array.from(bytes).map((b) => b.toString(16).padStart(2, '0')).join('');
}

export default function DemoInvestorFlow() {
  const [role, setRole] = useState<Role>('none');
  const [step, setStep] = useState<Step>('create');
  const [patient, setPatient] = useState<Patient | null>(null);
  const [consultations, setConsultations] = useState<MedicalConsultation[]>([]);
  const [updateAdded, setUpdateAdded] = useState<MedicalConsultation | null>(null);
  const [txHash, setTxHash] = useState('');
  const [isEncrypting, setIsEncrypting] = useState(false);
  const [encryptionKey, setEncryptionKey] = useState('');
  const [patientEmail, setPatientEmail] = useState('');

  const resetDemo = () => {
    setRole('none');
    setStep('create');
    setPatient(null);
    setConsultations([]);
    setUpdateAdded(null);
    setTxHash('');
    setIsEncrypting(false);
    setEncryptionKey('');
    setPatientEmail('');
  };

  const createPatientAccount = () => {
    const email = patientEmail || 'patient.demo@sante.bj';
    const newPatient: Patient = {
      name: 'Patient Démo',
      email,
      phone: '+229 97 00 00 00',
      walletBalance: 25000,
      npi: '1097000000000',
      avatar: 'PD',
    };
    setPatient(newPatient);
    setConsultations([]);
    setStep('patient_view');
  };

  const addAgentUpdate = async () => {
    const key = crypto.getRandomValues(new Uint8Array(32));
    const keyHex = Array.from(key).map((b) => b.toString(16).padStart(2, '0')).join('');
    const plaintext = JSON.stringify({
      diagnosis: 'Paludisme confirmé : Plasmodium falciparum',
      prescription: 'Artéméther + Luméfantrine 20/120mg',
      notes: 'Patient stabilisé sous traitement',
      doctor: 'Dr Jean Sossou',
      hospital: 'CHD Atlantique',
    });

    setIsEncrypting(true);
    await aesEncrypt(plaintext, keyHex);
    const hash = await generateSHA256(plaintext);
    const newConsultation: MedicalConsultation = {
      id: `cons-${Date.now()}`,
      date: new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' }),
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
      doctor: 'Dr Jean Sossou',
      hospital: 'CHD Atlantique',
      reason: 'Mise à jour agent de santé',
      diagnosis: 'Paludisme confirmé : Plasmodium falciparum',
      prescription: 'Artéméther + Luméfantrine 20/120mg',
      notes: 'Patient stabilisé sous traitement',
      verified: true,
      timestamp: Math.floor(Date.now() / 1000),
      hash,
    };

    setEncryptionKey(keyHex);
    setUpdateAdded(newConsultation);
    setConsultations((prev) => [newConsultation, ...prev]);
    setTxHash(randomTxHash());
    setIsEncrypting(false);
    setStep('patient_see_update');
  };

  const payInvoice = () => {
    setTxHash(randomTxHash());
    setStep('done');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-3 mb-4">
          <Activity className="w-6 h-6 text-[#059669]" />
          <div>
            <h2 className="font-bold text-lg text-[#1C1C1E] font-sans">Démo investisseurs — flux réel</h2>
            <p className="text-xs text-gray-500 font-sans">Patient, agent de santé et Bitcoin. Choisissez un rôle pour commencer.</p>
          </div>
        </div>

        {role === 'none' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button onClick={() => setRole('patient')} className="p-5 rounded-2xl border border-gray-100 bg-gray-50 hover:bg-white hover:shadow-sm transition-all text-left cursor-pointer">
              <UserPlus className="w-5 h-5 text-[#059669] mb-2" />
              <p className="font-bold text-sm text-[#1C1C1E] font-sans">Je suis le patient</p>
              <p className="text-xs text-gray-500 font-sans mt-1">Créer un compte et ouvrir le dossier médical</p>
            </button>
            <button onClick={() => setRole('agent')} className="p-5 rounded-2xl border border-gray-100 bg-gray-50 hover:bg-white hover:shadow-sm transition-all text-left cursor-pointer">
              <Stethoscope className="w-5 h-5 text-[#059669] mb-2" />
              <p className="font-bold text-sm text-[#1C1C1E] font-sans">Je suis l'agent de santé</p>
              <p className="text-xs text-gray-500 font-sans mt-1">Confirmer le traitement et mettre à jour le dossier</p>
            </button>
          </div>
        )}

        <AnimatePresence mode="wait">
          {role === 'patient' && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="flex items-center gap-2 text-xs font-semibold text-gray-500 font-sans">
                <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                Compte patient créé
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="lg:col-span-2 space-y-4">
                  <div className="bg-gray-50 border border-gray-100 rounded-2xl p-4">
                    <h3 className="font-bold text-sm text-[#1C1C1E] font-sans mb-2">Dossier médical chiffré</h3>
                    <div className="flex items-center gap-2 text-xs text-gray-600 font-sans mb-2">
                      <Lock className="w-4 h-4" />
                      Chiffrement AES-256 actif
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-600 font-sans">
                      <Eye className="w-4 h-4" />
                      Accès : patient uniquement
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-gray-500 font-sans uppercase tracking-wider">Consultations</h4>
                    {consultations.length === 0 && (
                      <p className="text-xs text-gray-500 font-sans">Aucune mise à jour confirmée pour l’instant.</p>
                    )}
                    {consultations.map((c) => (
                      <div key={c.id} className="p-4 rounded-2xl border border-gray-100 bg-white">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-bold text-[#1C1C1E] font-sans">{c.reason}</p>
                            <p className="text-xs text-gray-500 font-sans">{c.doctor} — {c.hospital}</p>
                          </div>
                          <span className="text-[10px] font-bold text-[#059669] bg-emerald-50 border border-emerald-100 px-2 py-1 rounded-lg font-sans">
                            Confirmé
                          </span>
                        </div>
                        {c.diagnosis && (
                          <p className="text-xs text-gray-600 font-sans mt-2">
                            <span className="font-semibold">Diagnostic :</span> {c.diagnosis}
                          </p>
                        )}
                        {c.prescription && (
                          <p className="text-xs text-gray-600 font-sans mt-1">
                            <span className="font-semibold">Prescription :</span> {c.prescription}
                          </p>
                        )}
                        {c.notes && (
                          <p className="text-xs text-gray-600 font-sans mt-1">
                            <span className="font-semibold">Notes :</span> {c.notes}
                          </p>
                        )}
                        <div className="mt-3 p-2 bg-gray-50 rounded-xl border border-gray-100">
                          <p className="text-[10px] text-gray-500 font-sans break-all">
                            <span className="font-semibold">Hash :</span> {c.hash}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-white rounded-2xl border border-gray-100 p-4 space-y-3">
                    <h4 className="text-xs font-bold text-gray-500 font-sans uppercase tracking-wider">Preuve patient</h4>
                    <p className="text-xs text-gray-500 font-sans">Partagez ce QR avec l’agent autorisé.</p>
                    <div className="flex justify-center">
                      <QRCodeSVG value={`santeplus://medical-record/${patient?.npi || 'unknown'}?token=SANTEPLUS-${patient?.npi || 'unknown'}-DEMO`} size={140} />
                    </div>
                  </div>

                  <div className="bg-emerald-50 border border-emerald-100 rounded-2xl p-4 space-y-2">
                    <h4 className="text-xs font-bold text-[#059669] font-sans">Statut</h4>
                    <p className="text-xs text-gray-700 font-sans">
                      Dossier bien verrouillé. Aucune modification extérieure n’est possible sans votre consentement.
                    </p>
                  </div>
                </div>
              </div>

              {step === 'patient_see_update' && updateAdded && (
                <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} className="bg-emerald-50 border border-emerald-100 rounded-2xl p-4 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#059669] font-sans">
                    <CheckCircle2 className="w-4 h-4" />
                    Mise à jour confirmée par l’agent de santé
                  </div>
                  <p className="text-xs text-gray-600 font-sans">Vous voyez maintenant la nouvelle entrée dans votre dossier.</p>
                </motion.div>
              )}

              {updateAdded && (
                <button onClick={() => setStep('bitcoin_pay')} className="inline-flex items-center gap-2 px-4 py-2 bg-[#059669] text-white rounded-2xl text-xs font-bold font-sans cursor-pointer">
                  <Bitcoin className="w-4 h-4" />
                  Payer la consultation en Bitcoin
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}

              {step === 'bitcoin_pay' && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-2xl border border-gray-100 p-4 space-y-3">
                  <h3 className="font-bold text-sm text-[#1C1C1E] font-sans">Paiement Lightning</h3>
                  <div className="flex items-center gap-3">
                    <QRCodeSVG value={`lightning:lnbc100u1p3xk...${txHash || 'demo'}`} size={140} />
                    <div className="text-xs text-gray-600 font-sans space-y-1">
                      <p>Montant : 5 000 XOF ≈ 8 330 sats</p>
                      <p>Statut : {txHash ? 'Payé' : 'En attente'}</p>
                      {txHash && (
                        <p className="break-all">
                          <span className="font-semibold">TXID :</span> {txHash}
                        </p>
                      )}
                    </div>
                  </div>
                  {!txHash && (
                    <button onClick={payInvoice} className="px-4 py-2 bg-[#059669] text-white rounded-2xl text-xs font-bold font-sans cursor-pointer">
                      Simuler paiement confirmé
                    </button>
                  )}
                </motion.div>
              )}

              {step === 'done' && (
                <div className="bg-white rounded-2xl border border-emerald-100 p-4 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#059669] font-sans">
                    <CheckCircle2 className="w-4 h-4" />
                    Paiement enregistré
                  </div>
                  <p className="text-xs text-gray-600 font-sans">La facture, le hash et la transaction sont conservés pour vérification.</p>
                  <button onClick={resetDemo} className="text-xs text-[#059669] font-bold font-sans cursor-pointer">Relancer la démo</button>
                </div>
              )}
            </motion.div>
          )}

          {role === 'agent' && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
              <div className="bg-gray-50 border border-gray-100 rounded-2xl p-4">
                <p className="text-xs text-gray-600 font-sans">
                  En tant qu’agent, vous ne modifiez pas un vieux dossier. Vous ajoutez une mise à jour horodatée et vérifiable.
                </p>
              </div>

              <div className="bg-white rounded-2xl border border-gray-100 p-4 space-y-3">
                <h3 className="font-bold text-sm text-[#1C1C1E] font-sans">Nouvelle mise à jour médicale</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input disabled value="Dr Jean Sossou" className="px-3 py-2 rounded-xl border border-gray-200 text-xs font-sans bg-gray-50" />
                  <input disabled value="CHD Atlantique" className="px-3 py-2 rounded-xl border border-gray-200 text-xs font-sans bg-gray-50" />
                </div>
                <input disabled value="Consultation de confirmation" className="px-3 py-2 rounded-xl border border-gray-200 text-xs font-sans bg-gray-50" />
                <textarea disabled value="Paludisme confirmé. Traitement initié. Patient sous monitoring." className="px-3 py-2 rounded-xl border border-gray-200 text-xs font-sans bg-gray-50" />
                <button onClick={addAgentUpdate} disabled={isEncrypting} className="inline-flex items-center gap-2 px-4 py-2 bg-[#059669] text-white rounded-2xl text-xs font-bold font-sans cursor-pointer disabled:opacity-60">
                  {isEncrypting ? 'Chiffrement...' : 'Confirmer et ancrer'}
                </button>
              </div>

              {updateAdded && (
                <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} className="bg-white rounded-2xl border border-gray-100 p-4 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#059669] font-sans">
                    <CheckCircle2 className="w-4 h-4" />
                    Mise à jour confirmée
                  </div>
                  <p className="text-xs text-gray-600 font-sans">Elle est maintenant visible côté patient et horodatée.</p>
                  <div className="p-2 bg-gray-50 rounded-xl border border-gray-100">
                    <p className="text-[10px] text-gray-500 font-sans break-all">
                      <span className="font-semibold">Hash :</span> {updateAdded.hash}
                    </p>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
