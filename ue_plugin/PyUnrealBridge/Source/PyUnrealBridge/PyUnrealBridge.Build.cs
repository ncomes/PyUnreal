// PyUnreal Bridge — Unreal Build Tool module rules.
//
// Editor-only module that exposes Animation Blueprint and Blueprint graph
// manipulation APIs to Python. This is the standalone C++ bridge for the
// PyUnreal library — no other plugins required.
//
// These UFUNCTION(BlueprintCallable) functions are auto-exposed to UE's
// Python interpreter, making them available as:
//   unreal.PyUnrealBlueprintLibrary.create_anim_blueprint(...)

using UnrealBuildTool;

public class PyUnrealBridge : ModuleRules
{
	public PyUnrealBridge(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		// --- Public Dependencies -------------------------------------------
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
			}
		);

		// --- Private Dependencies ------------------------------------------
		// AnimGraph + BlueprintGraph for graph node creation.
		// UnrealEd + Kismet for FBlueprintEditorUtils and transactions.
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"Slate",
				"SlateCore",
				"UnrealEd",
				"BlueprintGraph",
				"AnimGraph",
				"AnimGraphRuntime",
				"Kismet",
				"KismetCompiler",
				"ToolMenus",
				"AssetTools",
			}
		);
	}
}
