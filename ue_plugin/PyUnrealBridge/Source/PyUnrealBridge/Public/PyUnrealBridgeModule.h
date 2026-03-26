// PyUnreal Bridge Module — Public header.
//
// Minimal editor module that registers the PyUnrealBlueprintLibrary
// classes. The actual APIs live in the library headers — this module
// just ensures they get loaded.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

// Custom log category for PyUnreal bridge operations.
DECLARE_LOG_CATEGORY_EXTERN(LogPyUnreal, Log, All);

/**
 * Editor-only module that exposes Animation Blueprint and Blueprint graph
 * editing APIs to Python via UFUNCTION(BlueprintCallable).
 *
 * This is the standalone C++ bridge for the PyUnreal library.
 * No other plugins are required.
 */
class FPyUnrealBridgeModule : public IModuleInterface
{
public:

	/** Called when the module is loaded. */
	virtual void StartupModule() override;

	/** Called when the module is unloaded. */
	virtual void ShutdownModule() override;
};
