import React, { useState } from 'react';
import { Hospital, Review, ServicePrice } from '../types';
import { ArrowLeft, Star, Phone, MapPin, Clock, Calendar, Check, Send, ShieldCheck, HeartPulse, CreditCard, ShoppingCart, Zap, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { XOF_TO_SATS } from '../data';

interface HospitalDetailsProps {
  hospital: Hospital;
  onBack: () => void;
  onBookAppointment: () => void;
  onProceedToPayment: (selectedServices: ServicePrice[]) => void;
}

export default function HospitalDetails({
  hospital,
  onBack,
  onBookAppointment,
  onProceedToPayment,
}: HospitalDetailsProps) {
  const [reviews, setReviews] = useState<Review[]>(hospital.reviews);
  const [newAuthor, setNewAuthor] = useState('');
  const [newComment, setNewComment] = useState('');
  const [newRating, setNewRating] = useState(5);
  const [showReviewSuccess, setShowReviewSuccess] = useState(false);
  const [selectedServices, setSelectedServices] = useState<Set<number>>(new Set());

  const toggleService = (index: number) => {
    setSelectedServices(prev => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const selectAllServices = () => {
    if (selectedServices.size === hospital.priceList.length) {
      setSelectedServices(new Set());
    } else {
      setSelectedServices(new Set(hospital.priceList.map((_, i) => i)));
    }
  };

  const totalSelectedXOF = hospital.priceList
    .filter((_, i) => selectedServices.has(i))
    .reduce((sum, s) => sum + s.priceXOF, 0);
  const totalSelectedSats = Math.round(totalSelectedXOF * XOF_TO_SATS);

  const handleProceedToPayment = () => {
    const services = hospital.priceList.filter((_, i) => selectedServices.has(i));
    onProceedToPayment(services);
  };

  const handleSubmitReview = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAuthor.trim() || !newComment.trim()) return;

    const newReview: Review = {
      id: `r-new-${Date.now()}`,
      author: newAuthor,
      rating: newRating,
      date: 'Aujourd\'hui',
      comment: newComment,
    };

    setReviews([newReview, ...reviews]);
    setNewAuthor('');
    setNewComment('');
    setNewRating(5);
    setShowReviewSuccess(true);
    setTimeout(() => setShowReviewSuccess(false), 3000);
  };

  return (
    <div id="hospital-details-page" className="max-w-4xl mx-auto bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
      {/* Cover Image & Header */}
      <div className="relative h-64 md:h-80 bg-gray-900">
        <img
          src={hospital.image}
          alt={hospital.name}
          className="w-full h-full object-cover opacity-80"
          referrerPolicy="no-referrer"
        />
        {/* Back Button Overlay */}
        <button
          onClick={onBack}
          className="absolute top-5 left-5 p-2.5 bg-white/90 backdrop-blur-md rounded-full text-gray-800 hover:bg-white shadow-md transition-all cursor-pointer"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>

        {/* Floating Verified Tag */}
        {hospital.isVerified && (
          <div className="absolute top-5 right-5 px-3 py-1.5 bg-white/95 backdrop-blur-md border border-amber-200 rounded-full text-[#FF8A00] font-bold font-sans text-xs flex items-center gap-1 shadow-md">
            <ShieldCheck className="w-4 h-4 text-[#FF8A00]" />
            Établissement Agréé MSP
          </div>
        )}

        {/* Hospital Title Block Overlay at the bottom */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent p-6 text-white">
          <div className="flex items-center gap-2 mb-1.5">
            <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-sans font-semibold uppercase tracking-wider ${
              hospital.type === 'public' ? 'bg-[#059669] text-white' : 'bg-[#FF8A00] text-white'
            }`}>
              {hospital.type === 'public' ? 'Secteur Public' : 'Clinique Privée'}
            </span>
            <span className="text-xs text-gray-300 font-sans font-medium">• {hospital.distance} de vous</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold font-sans tracking-tight">{hospital.name}</h1>
        </div>
      </div>

      {/* Main Content Sections */}
      <div className="p-6 md:p-8 grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left Column: Info, Pricing, Services */}
        <div className="md:col-span-7 space-y-8">
          {/* Quick Contact & Info */}
          <div className="p-5 bg-gray-50 rounded-2xl space-y-4 border border-gray-100">
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-gray-400 font-sans">Adresse</p>
                <p className="text-sm font-sans font-semibold text-[#1C1C1E]">{hospital.address}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Phone className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-gray-400 font-sans">Téléphone Officiel</p>
                <p className="text-sm font-sans font-semibold text-[#1C1C1E]">{hospital.phone}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Clock className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-gray-400 font-sans">Horaires d'Ouverture</p>
                <p className="text-sm font-sans font-semibold text-[#1C1C1E]">{hospital.hours}</p>
              </div>
            </div>
          </div>

          {/* List of Services */}
          <div>
            <h3 className="text-lg font-sans font-bold text-[#1C1C1E] mb-3 flex items-center gap-2">
              <HeartPulse className="w-5 h-5 text-[#059669]" />
              Spécialités & Services disponibles
            </h3>
            <div className="flex flex-wrap gap-2">
              {hospital.services.map((service, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-emerald-50 border border-emerald-100 text-[#059669] rounded-xl text-xs font-sans font-medium"
                >
                  {service}
                </span>
              ))}
            </div>
          </div>

          {/* Official Grille de Tarifs — Interactive Selection */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-sans font-bold text-[#1C1C1E] flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-[#00D26A]" />
                Grille Tarifaire Transparente
              </h3>
              <button
                onClick={selectAllServices}
                className="text-[11px] font-sans font-bold text-[#059669] hover:text-[#059669]/80 bg-emerald-50 hover:bg-emerald-100 px-3 py-1 rounded-lg border border-emerald-100 transition-all cursor-pointer"
              >
                {selectedServices.size === hospital.priceList.length ? 'Tout désélectionner' : 'Tout sélectionner'}
              </button>
            </div>
            <p className="text-xs text-gray-500 font-sans mb-3">
              ✅ Cochez les actes médicaux que vous souhaitez régler, puis cliquez sur <strong>"Payer maintenant"</strong> pour procéder au paiement sécurisé.
            </p>
            <div className="border border-gray-100 rounded-2xl overflow-hidden divide-y divide-gray-100">
              <div className="grid grid-cols-12 bg-gray-50 p-3.5 text-xs font-bold text-gray-500 uppercase font-sans">
                <span className="col-span-1"></span>
                <span className="col-span-6">Acte Médical / Examen</span>
                <span className="col-span-3 text-right">Franc CFA (XOF)</span>
                <span className="col-span-2 text-right">Satoshis ⚡</span>
              </div>
              {hospital.priceList.map((item, index) => {
                const isSelected = selectedServices.has(index);
                return (
                  <button
                    key={index}
                    type="button"
                    onClick={() => toggleService(index)}
                    className={`w-full grid grid-cols-12 p-3.5 text-sm items-center transition-all duration-200 cursor-pointer text-left ${
                      isSelected
                        ? 'bg-emerald-50/70 hover:bg-emerald-50'
                        : 'hover:bg-gray-50/50'
                    }`}
                  >
                    <span className="col-span-1 flex items-center justify-center">
                      <span className={`w-5 h-5 rounded-lg border-2 flex items-center justify-center transition-all duration-200 ${
                        isSelected
                          ? 'bg-[#00D26A] border-[#00D26A] text-white scale-110'
                          : 'border-gray-300 bg-white hover:border-gray-400'
                      }`}>
                        {isSelected && <Check className="w-3 h-3" />}
                      </span>
                    </span>
                    <span className={`col-span-6 font-sans font-medium transition-colors ${
                      isSelected ? 'text-[#059669]' : 'text-gray-700'
                    }`}>{item.name}</span>
                    <span className={`col-span-3 text-right font-sans font-semibold transition-colors ${
                      isSelected ? 'text-[#059669]' : 'text-[#1C1C1E]'
                    }`}>
                      {item.priceXOF.toLocaleString('fr-FR')} XOF
                    </span>
                    <span className={`col-span-2 text-right font-mono text-xs font-bold transition-colors ${
                      isSelected ? 'text-[#059669]' : 'text-[#00D26A]'
                    }`}>
                      {item.priceSats.toLocaleString()}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Sticky Cart Summary */}
            <AnimatePresence>
              {selectedServices.size > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 20, scale: 0.95 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                  className="mt-4 p-4 bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl shadow-lg border border-slate-700"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-xl bg-[#00D26A]/20 flex items-center justify-center">
                        <ShoppingCart className="w-4 h-4 text-[#00D26A]" />
                      </div>
                      <div>
                        <p className="text-[10px] text-gray-400 uppercase tracking-wider font-bold font-sans">Panier de soins</p>
                        <p className="text-xs text-gray-300 font-sans">
                          {selectedServices.size} acte{selectedServices.size > 1 ? 's' : ''} sélectionné{selectedServices.size > 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-black font-sans text-[#00D26A]">
                        {totalSelectedXOF.toLocaleString('fr-FR')} XOF
                      </p>
                      <p className="text-[11px] font-mono text-amber-400">
                        {totalSelectedSats.toLocaleString()} Sats ⚡
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={handleProceedToPayment}
                    className="w-full py-3.5 bg-[#00D26A] hover:bg-[#00D26A]/90 text-white font-extrabold font-sans text-sm rounded-xl shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer"
                  >
                    <Zap className="w-5 h-5 fill-white" />
                    Payer maintenant — {totalSelectedXOF.toLocaleString('fr-FR')} XOF
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Right Column: Actions & Patient Reviews */}
        <div className="md:col-span-5 space-y-8">
          {/* CRITICAL ACTIONS PANEL */}
          <div className="p-6 border border-gray-200 rounded-3xl bg-white shadow-xs space-y-4 sticky top-6">
            <h3 className="text-md font-bold font-sans text-gray-800">Parcours de Soins Citoyen</h3>
            <p className="text-xs text-gray-500 font-sans leading-relaxed">
              Sélectionnez les actes médicaux dans la <strong>grille tarifaire</strong> ci-contre, puis cliquez sur <strong>"Payer maintenant"</strong>. Vous pouvez aussi prendre un rendez-vous en ligne.
            </p>

            {/* BUTTON 1 : Prendre Rendez-vous */}
            <button
              onClick={onBookAppointment}
              className="w-full py-3.5 px-4 bg-[#059669] hover:bg-[#059669]/90 text-white font-sans font-bold rounded-2xl shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <Calendar className="w-5 h-5" />
              Prendre Rendez-vous en ligne
            </button>

            {/* BUTTON 2 : Payer les actes sélectionnés ou en attente */}
            <button
              onClick={handleProceedToPayment}
              className={`w-full py-3.5 px-4 font-sans font-bold rounded-2xl shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer ${
                selectedServices.size > 0
                  ? 'bg-[#00D26A] hover:bg-[#00D26A]/95 text-white'
                  : 'bg-[#00D26A] hover:bg-[#00D26A]/95 text-white'
              }`}
            >
              {selectedServices.size > 0 ? (
                <>
                  <Zap className="w-5 h-5 fill-white" />
                  <span>Payer {totalSelectedXOF.toLocaleString('fr-FR')} XOF ⚡</span>
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 fill-white" />
                  <span>Payer mes frais médicaux ⚡</span>
                </>
              )}
            </button>

            {/* Selected services summary */}
            {selectedServices.size > 0 && (
              <div className="p-3 bg-emerald-50 border border-emerald-100 rounded-xl space-y-1.5">
                <p className="text-[10px] text-emerald-700 uppercase font-bold tracking-wider font-sans flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  {selectedServices.size} acte{selectedServices.size > 1 ? 's' : ''} sélectionné{selectedServices.size > 1 ? 's' : ''}
                </p>
                {hospital.priceList.filter((_, i) => selectedServices.has(i)).map((s, idx) => (
                  <p key={idx} className="text-[11px] text-emerald-800 font-sans flex justify-between">
                    <span className="truncate mr-2">{s.name}</span>
                    <span className="font-semibold whitespace-nowrap">{s.priceXOF.toLocaleString('fr-FR')} XOF</span>
                  </p>
                ))}
                <div className="border-t border-emerald-200 pt-1 mt-1 flex justify-between text-xs font-bold text-emerald-900">
                  <span>Total</span>
                  <span>{totalSelectedXOF.toLocaleString('fr-FR')} XOF</span>
                </div>
              </div>
            )}
          </div>

          {/* REVIEWS SECTION */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-sans font-bold text-[#1C1C1E]">Avis des Patients</h3>
              <div className="flex items-center text-[#FF8A00]">
                <Star className="w-4 h-4 fill-current" />
                <span className="text-sm font-bold font-sans ml-1">{hospital.rating}</span>
                <span className="text-xs text-gray-400 font-sans ml-1">({reviews.length})</span>
              </div>
            </div>

            {/* List of Reviews */}
            <div className="space-y-3.5 max-h-[280px] overflow-y-auto pr-1">
              {reviews.map((rev) => (
                <div key={rev.id} className="p-4 bg-white border border-gray-100 rounded-2xl shadow-2xs">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold font-sans text-gray-800">{rev.author}</span>
                    <span className="text-[10px] text-gray-400 font-sans">{rev.date}</span>
                  </div>
                  <div className="flex items-center text-amber-400 mb-2">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`w-3 h-3 ${i < rev.rating ? 'fill-current text-[#FF8A00]' : 'text-gray-200'}`}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600 font-sans leading-relaxed">{rev.comment}</p>
                </div>
              ))}
            </div>

            {/* Leave a Review Form */}
            <div className="p-4 bg-gray-50 rounded-2xl border border-gray-100">
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 font-sans">Laisser un avis</h4>
              <form onSubmit={handleSubmitReview} className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    required
                    placeholder="Votre nom complet"
                    value={newAuthor}
                    onChange={(e) => setNewAuthor(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-white border border-gray-200 rounded-xl font-sans focus:outline-none focus:ring-1 focus:ring-[#059669]"
                  />
                  <div className="flex items-center justify-end gap-1 bg-white px-2.5 py-1 border border-gray-200 rounded-xl">
                    <span className="text-[10px] font-sans font-medium text-gray-400 mr-1">Note :</span>
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        type="button"
                        key={star}
                        onClick={() => setNewRating(star)}
                        className="p-0.5 cursor-pointer text-[#FF8A00] hover:scale-110 transition-all"
                      >
                        <Star className={`w-3.5 h-3.5 ${star <= newRating ? 'fill-current' : 'text-gray-200'}`} />
                      </button>
                    ))}
                  </div>
                </div>
                <textarea
                  required
                  placeholder="Partagez votre expérience d'accueil ou de soins..."
                  rows={2}
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-white border border-gray-200 rounded-xl font-sans focus:outline-none focus:ring-1 focus:ring-[#059669] resize-none"
                ></textarea>

                <button
                  type="submit"
                  className="w-full py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-sans font-semibold flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                  Publier l'avis
                </button>
              </form>

              {showReviewSuccess && (
                <div className="mt-2.5 p-2 bg-emerald-50 border border-emerald-100 text-[#00D26A] text-xs font-medium font-sans rounded-xl flex items-center gap-1.5 justify-center">
                  <Check className="w-3.5 h-3.5" />
                  Votre avis a été publié avec succès.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
