// PyUnreal Bridge Module — Startup/shutdown implementation.
//
// Minimal module that just logs its presence. The actual work is done
// by the BlueprintFunctionLibrary classes which are auto-registered
// by UE's reflection system.

#include "PyUnrealBridgeModule.h"

// Define our custom log category.
DEFINE_LOG_CATEGORY(LogPyUnreal);

#define LOCTEXT_NAMESPACE "FPyUnrealBridgeModule"


void FPyUnrealBridgeModule::StartupModule()
{
	UE_LOG(LogPyUnreal, Log, TEXT("PyUnrealBridge: Module loaded — AnimBP graph APIs available for Python"));
}


void FPyUnrealBridgeModule::ShutdownModule()
{
	UE_LOG(LogPyUnreal, Log, TEXT("PyUnrealBridge: Module unloaded"));
}


#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FPyUnrealBridgeModule, PyUnrealBridge)
