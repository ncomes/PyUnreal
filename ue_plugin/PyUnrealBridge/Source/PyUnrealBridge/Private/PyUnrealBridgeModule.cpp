// PyUnreal Bridge Module — Startup/shutdown implementation.
//
// On startup, enables Python Remote Execution so that external tools
// (MCP servers, IDE extensions) can communicate with UE's Python
// interpreter over the network. The actual API functions are in the
// BlueprintFunctionLibrary classes, auto-registered by UE's reflection system.

#include "PyUnrealBridgeModule.h"
#include "Misc/ConfigCacheIni.h"

// Define our custom log category.
DEFINE_LOG_CATEGORY(LogPyUnreal);

#define LOCTEXT_NAMESPACE "FPyUnrealBridgeModule"


/**
 * Enable UE's Python Remote Execution if not already on.
 *
 * Remote Execution allows external processes (MCP servers, IDE tools) to
 * send Python code to UE's interpreter over TCP. Without it, PyUnreal
 * can only be used from UE's built-in Python console.
 *
 * The setting lives in DefaultEngine.ini under [/Script/PythonScriptPlugin.PythonScriptPluginSettings].
 * We flip it via the CDO so it takes effect immediately and persists.
 */
static void EnsureRemoteExecution()
{
	// PythonScriptPluginSettings is part of PythonScriptPlugin which is
	// an optional dependency. Use FindObject to avoid a hard link.
	UClass* SettingsClass = FindObject<UClass>(
		nullptr, TEXT("/Script/PythonScriptPlugin.PythonScriptPluginSettings"));

	if (!SettingsClass)
	{
		UE_LOG(LogPyUnreal, Log,
			TEXT("PythonScriptPlugin not loaded — skipping Remote Execution setup"));
		return;
	}

	UObject* CDO = SettingsClass->GetDefaultObject();
	if (!CDO)
	{
		return;
	}

	// The property is "bRemoteExecution" in C++ / "remote_execution" in Python.
	FBoolProperty* RemoteProp = CastField<FBoolProperty>(
		SettingsClass->FindPropertyByName(TEXT("bRemoteExecution")));

	if (!RemoteProp)
	{
		UE_LOG(LogPyUnreal, Warning,
			TEXT("Could not find bRemoteExecution property — UE version mismatch?"));
		return;
	}

	bool bCurrentValue = RemoteProp->GetPropertyValue_InContainer(CDO);
	if (!bCurrentValue)
	{
		RemoteProp->SetPropertyValue_InContainer(CDO, true);
		CDO->SaveConfig();
		UE_LOG(LogPyUnreal, Log,
			TEXT("PyUnrealBridge: Enabled Python Remote Execution"));
	}
	else
	{
		UE_LOG(LogPyUnreal, Log,
			TEXT("PyUnrealBridge: Python Remote Execution already enabled"));
	}
}


void FPyUnrealBridgeModule::StartupModule()
{
	UE_LOG(LogPyUnreal, Log,
		TEXT("PyUnrealBridge: Module loaded — AnimBP graph APIs available for Python"));

	// Enable Remote Execution so MCP / external tools can reach UE's Python.
	EnsureRemoteExecution();
}


void FPyUnrealBridgeModule::ShutdownModule()
{
	UE_LOG(LogPyUnreal, Log, TEXT("PyUnrealBridge: Module unloaded"));
}


#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FPyUnrealBridgeModule, PyUnrealBridge)
