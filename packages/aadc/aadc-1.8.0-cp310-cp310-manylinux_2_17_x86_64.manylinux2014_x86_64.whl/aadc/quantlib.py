import os, sys

from aadc._aadc_core.QuantLib import *


Leg = list
CalibrationSet = list

__version__ = "AAAA"
__hexversion__ = "BBBB"

RelinkableHandle_QuantLib_YieldTermStructure_t.__getattr__ = lambda self, name: getattr(self.currentLink(), name)
Handle_QuantLib_YieldTermStructure_t.__getattr__ = lambda self, name: getattr(self.currentLink(), name)
####import aadc.swap_i
_MakeVanillaSwap = MakeVanillaSwap
def MakeVanillaSwap(swapTenor, iborIndex, fixedRate, forwardStart,
    receiveFixed=None, swapType=None, Nominal=None, settlementDays=None,
    effectiveDate=None, terminationDate=None, dateGenerationRule=None,
    fixedLegTenor=None, fixedLegCalendar=None, fixedLegConvention=None,
    fixedLegDayCount=None, floatingLegTenor=None, floatingLegCalendar=None,
    floatingLegConvention=None, floatingLegDayCount=None, floatingLegSpread=None,
    discountingTermStructure=None, pricingEngine=None,
    fixedLegTerminationDateConvention=None,  fixedLegDateGenRule=None,
    fixedLegEndOfMonth=None, fixedLegFirstDate=None, fixedLegNextToLastDate=None,
    floatingLegTerminationDateConvention=None, floatingLegDateGenRule=None,
    floatingLegEndOfMonth=None, floatingLegFirstDate=None, floatingLegNextToLastDate=None,
    withIndexedCoupons=None):
    mv = _MakeVanillaSwap(swapTenor, iborIndex, fixedRate, forwardStart)
    if receiveFixed is not None:
        mv.receiveFixed(receiveFixed)
    if swapType is not None:
        mv.withType(swapType)
    if Nominal is not None:
        mv.withNominal(Nominal)
    if settlementDays is not None:
        mv.withSettlementDays(settlementDays)
    if effectiveDate is not None:
        mv.withEffectiveDate(effectiveDate)
    if terminationDate is not None:
        mv.withTerminationDate(terminationDate)
    if dateGenerationRule is not None:
        mv.withRule(dateGenerationRule)
    if fixedLegTenor is not None:
        mv.withFixedLegTenor(fixedLegTenor)
    if fixedLegCalendar is not None:
        mv.withFixedLegCalendar(fixedLegCalendar)
    if fixedLegConvention is not None:
        mv.withFixedLegConvention(fixedLegConvention)
    if fixedLegDayCount is not None:
        mv.withFixedLegDayCount(fixedLegDayCount)
    if floatingLegTenor is not None:
        mv.withFloatingLegTenor(floatingLegTenor)
    if floatingLegCalendar is not None:
        mv.withFloatingLegCalendar(floatingLegCalendar)
    if floatingLegConvention is not None:
        mv.withFloatingLegConvention(floatingLegConvention)
    if floatingLegDayCount is not None:
        mv.withFloatingLegDayCount(floatingLegDayCount)
    if floatingLegSpread is not None:
        mv.withFloatingLegSpread(floatingLegSpread)
    if discountingTermStructure is not None:
        mv.withDiscountingTermStructure(discountingTermStructure)
    if pricingEngine is not None:
        mv.withPricingEngine(pricingEngine)
    if fixedLegTerminationDateConvention is not None:
        mv.withFixedLegTerminationDateConvention(fixedLegTerminationDateConvention)
    if fixedLegDateGenRule is not None:
        mv.withFixedLegRule(fixedLegDateGenRule)
    if fixedLegEndOfMonth is not None:
        mv.withFixedLegEndOfMonth(fixedLegEndOfMonth)
    if fixedLegFirstDate is not None:
        mv.withFixedLegFirstDate(fixedLegFirstDate)
    if fixedLegNextToLastDate is not None:
        mv.withFixedLegNextToLastDate(fixedLegNextToLastDate)
    if floatingLegTerminationDateConvention is not None:
        mv.withFloatingLegTerminationDateConvention(floatingLegTerminationDateConvention)
    if floatingLegDateGenRule is not None:
        mv.withFloatingLegRule(floatingLegDateGenRule)
    if floatingLegEndOfMonth is not None:
        mv.withFloatingLegEndOfMonth(floatingLegEndOfMonth)
    if floatingLegFirstDate is not None:
        mv.withFloatingLegFirstDate(floatingLegFirstDate)
    if floatingLegNextToLastDate is not None:
        mv.withFloatingLegNextToLastDate(floatingLegNextToLastDate)
    if withIndexedCoupons is not None:
        mv.withIndexedCoupons(withIndexedCoupons)
    return mv.makeVanillaSwap()

# %rename (_MakeOIS) MakeOIS;
_MakeOIS = MakeOIS

def MakeOIS(swapTenor, overnightIndex, fixedRate, fwdStart=Period(0, Days),
            receiveFixed=True,
            swapType=Swap.Payer,
            nominal=1.0,
            settlementDays=2,
            effectiveDate=None,
            terminationDate=None,
            dateGenerationRule=DateGeneration.Backward,
            paymentFrequency=Annual,
            paymentAdjustmentConvention=Following,
            paymentLag=0,
            paymentCalendar=None,
            endOfMonth=True,
            fixedLegDayCount=None,
            overnightLegSpread=0.0,
            discountingTermStructure=None,
            telescopicValueDates=False,
            pricingEngine=None,
            averagingMethod=None):

    mv = _MakeOIS(swapTenor, overnightIndex, fixedRate, fwdStart)

    if not receiveFixed:
        mv.receiveFixed(receiveFixed)
    if swapType != Swap.Payer:
        mv.withType(swapType)
    if nominal != 1.0:
        mv.withNominal(nominal)
    if settlementDays != 2:
        mv.withSettlementDays(settlementDays)
    if effectiveDate is not None:
        mv.withEffectiveDate(effectiveDate)
    if terminationDate is not None:
        mv.withTerminationDate(terminationDate)
    if dateGenerationRule != DateGeneration.Backward:
        mv.withRule(dateGenerationRule)
    if paymentFrequency != Annual:
        mv.withPaymentFrequency(paymentFrequency)
    if paymentAdjustmentConvention != Following:
        mv.withPaymentAdjustment(paymentAdjustmentConvention)
    if paymentLag != 0:
        mv.withPaymentLag(paymentLag)
    if paymentCalendar is not None:
        mv.withPaymentCalendar(paymentCalendar)
    if not endOfMonth:
        mv.withEndOfMonth(endOfMonth)
    if fixedLegDayCount is not None:
        mv.withFixedLegDayCount(fixedLegDayCount)
    else:
        mv.withFixedLegDayCount(overnightIndex.dayCounter())
    if overnightLegSpread != 0.0:
        mv.withOvernightLegSpread(overnightLegSpread)
    if discountingTermStructure is not None:
        mv.withDiscountingTermStructure(discountingTermStructure)
    if telescopicValueDates:
        mv.withTelescopicValueDates(telescopicValueDates)
    if averagingMethod is not None:
        mv.withAveragingMethod(averagingMethod)
    if pricingEngine is not None:
        mv.withPricingEngine(pricingEngine)

    return mv.makeOIS()

_MakeSchedule = MakeSchedule

def MakeSchedule(effectiveDate=None,terminationDate=None,tenor=None,
    frequency=None,calendar=None,convention=None,terminalDateConvention=None,
    rule=None,forwards=False,backwards=False,
    endOfMonth=None,firstDate=None,nextToLastDate=None):
    ms = _MakeSchedule()
    if effectiveDate is not None:
        ms.fromDate(effectiveDate)
    if terminationDate is not None:
        ms.to(terminationDate)
    if tenor is not None:
        ms.withTenor(tenor)
    if frequency is not None:
        ms.withFrequency(frequency)
    if calendar is not None:
        ms.withCalendar(calendar)
    if convention is not None:
        ms.withConvention(convention)
    if terminalDateConvention is not None:
        ms.withTerminationDateConvention(terminalDateConvention)
    if rule is not None:
        ms.withRule(rule)
    if forwards:
        ms.forwards()
    if backwards:
        ms.backwards()
    if endOfMonth is not None:
        ms.endOfMonth(endOfMonth)
    if firstDate is not None:
        ms.withFirstDate(firstDate)
    if nextToLastDate is not None:
        ms.withNextToLastDate(nextToLastDate)
    return ms.schedule()

def BinomialVanillaEngine(process, type, steps):
    type = type.lower()
    if type == "crr" or type == "coxrossrubinstein":
        cls = BinomialCRRVanillaEngine
    elif type == "jr" or type == "jarrowrudd":
        cls = BinomialJRVanillaEngine
    elif type == "eqp":
        cls = BinomialEQPVanillaEngine
    elif type == "trigeorgis":
        cls = BinomialTrigeorgisVanillaEngine
    elif type == "tian":
        cls = BinomialTianVanillaEngine
    elif type == "lr" or type == "leisenreimer":
        cls = BinomialLRVanillaEngine
    elif type == "j4" or type == "joshi4":
        cls = BinomialJ4VanillaEngine
    else:
        raise RuntimeError("unknown binomial engine type: %s" % type);
    return cls(process, steps)

def MCEuropeanEngine(process,
                        traits,
                        timeSteps=None,
                        timeStepsPerYear=None,
                        brownianBridge=False,
                        antitheticVariate=False,
                        requiredSamples=None,
                        requiredTolerance=None,
                        maxSamples=None,
                        seed=0):
    traits = traits.lower()
    if traits == "pr" or traits == "pseudorandom":
        cls = MCPREuropeanEngine
    elif traits == "ld" or traits == "lowdiscrepancy":
        cls = MCLDEuropeanEngine
    else:
        raise RuntimeError("unknown MC traits: %s" % traits);
    return cls(process,
                timeSteps,
                timeStepsPerYear,
                brownianBridge,
                antitheticVariate,
                requiredSamples,
                requiredTolerance,
                maxSamples,
                seed)

def MCAmericanEngine(process,
                        traits,
                        timeSteps=None,
                        timeStepsPerYear=None,
                        antitheticVariate=False,
                        controlVariate=False,
                        requiredSamples=None,
                        requiredTolerance=None,
                        maxSamples=None,
                        seed=0,
                        polynomOrder=2,
                        polynomType=LsmBasisSystem.Monomial,
                        nCalibrationSamples=2048,
                        antitheticVariateCalibration=None,
                        seedCalibration=None):
    traits = traits.lower()
    if traits == "pr" or traits == "pseudorandom":
        cls = MCPRAmericanEngine
    elif traits == "ld" or traits == "lowdiscrepancy":
        cls = MCLDAmericanEngine
    else:
        raise RuntimeError("unknown MC traits: %s" % traits);
    return cls(process,
                timeSteps,
                timeStepsPerYear,
                antitheticVariate,
                controlVariate,
                requiredSamples,
                requiredTolerance,
                maxSamples,
                seed,
                polynomOrder,
                polynomType,
                nCalibrationSamples,
                antitheticVariateCalibration,
                seedCalibration if seedCalibration is not None else nullInt())

def MCEuropeanHestonEngine(process,
                            traits,
                            timeSteps=None,
                            timeStepsPerYear=None,
                            antitheticVariate=False,
                            requiredSamples=None,
                            requiredTolerance=None,
                            maxSamples=None,
                            seed=0):
    traits = traits.lower()
    if traits == "pr" or traits == "pseudorandom":
        cls = MCPREuropeanHestonEngine
    elif traits == "ld" or traits == "lowdiscrepancy":
        cls = MCLDEuropeanHestonEngine
    else:
        raise RuntimeError("unknown MC traits: %s" % traits);
    return cls(process,
                timeSteps,
                timeStepsPerYear,
                antitheticVariate,
                requiredSamples,
                requiredTolerance,
                maxSamples,
                seed)

def MCDigitalEngine(process,
                    traits,
                    timeSteps=None,
                    timeStepsPerYear=None,
                    brownianBridge=False,
                    antitheticVariate=False,
                    requiredSamples=None,
                    requiredTolerance=None,
                    maxSamples=None,
                    seed=0):
    traits = traits.lower()
    if traits == "pr" or traits == "pseudorandom":
        cls = MCPRDigitalEngine
    elif traits == "ld" or traits == "lowdiscrepancy":
        cls = MCLDDigitalEngine
    else:
        raise RuntimeError("unknown MC traits: %s" % traits);
    return cls(process,
                timeSteps,
                timeStepsPerYear,
                brownianBridge,
                antitheticVariate,
                requiredSamples,
                requiredTolerance,
                maxSamples,
                seed)

def MCForwardEuropeanBSEngine(process,
                                traits,
                                timeSteps=None,
                                timeStepsPerYear=None,
                                brownianBridge=False,
                                antitheticVariate=False,
                                requiredSamples=None,
                                requiredTolerance=None,
                                maxSamples=None,
                                seed=0):
    traits = traits.lower()
    if traits == "pr" or traits == "pseudorandom":
        cls = MCPRForwardEuropeanBSEngine
    elif traits == "ld" or traits == "lowdiscrepancy":
        cls = MCLDForwardEuropeanBSEngine
    else:
        raise RuntimeError("unknown MC traits: %s" % traits);
    return cls(process,
                timeSteps,
                timeStepsPerYear,
                brownianBridge,
                antitheticVariate,
                requiredSamples,
                requiredTolerance,
                maxSamples,
                seed)

def MCForwardEuropeanHestonEngine(process,
                                    traits,
                                    timeSteps=None,
                                    timeStepsPerYear=None,
                                    antitheticVariate=False,
                                    requiredSamples=None,
                                    requiredTolerance=None,
                                    maxSamples=None,
                                    seed=0,
                                    controlVariate=False):
    traits = traits.lower()
    if traits == "pr" or traits == "pseudorandom":
        cls = MCPRForwardEuropeanHestonEngine
    elif traits == "ld" or traits == "lowdiscrepancy":
        cls = MCLDForwardEuropeanHestonEngine
    else:
        raise RuntimeError("unknown MC traits: %s" % traits);
    return cls(process,
                timeSteps,
                timeStepsPerYear,
                antitheticVariate,
                requiredSamples,
                requiredTolerance,
                maxSamples,
                seed,
                controlVariate)

def MCEuropeanGJRGARCHEngine(process,
                                traits,
                                timeSteps=None,
                                timeStepsPerYear=None,
                                antitheticVariate=False,
                                requiredSamples=None,
                                requiredTolerance=None,
                                maxSamples=None,
                                seed=0):
    traits = traits.lower()
    if traits == "pr" or traits == "pseudorandom":
        cls = MCPREuropeanGJRGARCHEngine
    elif traits == "ld" or traits == "lowdiscrepancy":
        cls = MCLDEuropeanGJRGARCHEngine
    else:
        raise RuntimeError("unknown MC traits: %s" % traits);
    return cls(process,
                timeSteps,
                timeStepsPerYear,
                antitheticVariate,
                requiredSamples,
                requiredTolerance,
                maxSamples,
                seed)
