// PyUnreal EventGraph Operations — Implementation.
//
// Implements the EventGraph node creation and pin wiring functions.
// These let you programmatically build Blueprint EventGraphs — adding
// event nodes, function calls, cast nodes, variable get/set nodes,
// and wiring them together via pin connections.
//
// All node IDs use the node's FGuid serialized to a stable string.
// This allows Python code to reference nodes by ID when wiring pins.
//
// Key UE classes used:
//   - UK2Node_Event for event nodes (BeginPlay, InitializeAnimation, etc.)
//   - UK2Node_CallFunction for function call nodes
//   - UK2Node_DynamicCast for cast nodes
//   - UK2Node_VariableGet / UK2Node_VariableSet for variable access
//   - UEdGraphSchema_K2::TryCreateConnection() for pin wiring

#include "PyUnrealBlueprintLibrary.h"
#include "PyUnrealBridgeModule.h"

#include "Engine/Blueprint.h"
#include "Animation/AnimBlueprint.h"

#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraph/EdGraphPin.h"
#include "EdGraphSchema_K2.h"

#include "K2Node_Event.h"
#include "K2Node_CallFunction.h"
#include "K2Node_DynamicCast.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"

#include "Kismet2/BlueprintEditorUtils.h"
#include "ScopedTransaction.h"


// =============================================================================
// Internal Helpers — EventGraph
// =============================================================================

UEdGraph* UPyUnrealBlueprintLibrary::GetEventGraph(UBlueprint* Blueprint)
{
	if (!Blueprint)
	{
		return nullptr;
	}

	// The EventGraph is the first UbergraphPage.
	if (Blueprint->UbergraphPages.Num() > 0)
	{
		return Blueprint->UbergraphPages[0];
	}

	return nullptr;
}


UEdGraphNode* UPyUnrealBlueprintLibrary::FindNodeById(
	UBlueprint* Blueprint,
	const FString& NodeId)
{
	if (!Blueprint)
	{
		return nullptr;
	}

	// Parse the string back to a FGuid.
	FGuid TargetGuid;
	if (!FGuid::Parse(NodeId, TargetGuid))
	{
		UE_LOG(LogPyUnreal, Error, TEXT("FindNodeById: Invalid GUID string '%s'"), *NodeId);
		return nullptr;
	}

	// Search all UbergraphPages (there may be more than one).
	for (UEdGraph* Graph : Blueprint->UbergraphPages)
	{
		if (!Graph)
		{
			continue;
		}

		for (UEdGraphNode* Node : Graph->Nodes)
		{
			if (Node && Node->NodeGuid == TargetGuid)
			{
				return Node;
			}
		}
	}

	return nullptr;
}


FString UPyUnrealBlueprintLibrary::NodeIdToString(const FGuid& Guid)
{
	return Guid.ToString();
}


// =============================================================================
// Add Event Node
// =============================================================================

FString UPyUnrealBlueprintLibrary::AddEventNode(
	UBlueprint* Blueprint,
	const FString& EventName)
{
	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddEventNode: Blueprint is null"));
		return FString();
	}

	UEdGraph* EventGraph = GetEventGraph(Blueprint);
	if (!EventGraph)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddEventNode: No EventGraph found in '%s'"),
			*Blueprint->GetName());
		return FString();
	}

	// Check if this event already exists in the graph.
	for (UEdGraphNode* Node : EventGraph->Nodes)
	{
		UK2Node_Event* ExistingEvent = Cast<UK2Node_Event>(Node);
		if (ExistingEvent && ExistingEvent->EventReference.GetMemberName().ToString() == EventName)
		{
			UE_LOG(LogPyUnreal, Log,
				TEXT("AddEventNode: Event '%s' already exists, returning existing node"),
				*EventName);
			return NodeIdToString(ExistingEvent->NodeGuid);
		}
	}

	FScopedTransaction Transaction(FText::FromString(
		FString::Printf(TEXT("PyUnreal: Add Event '%s'"), *EventName)));

	EventGraph->Modify();

	// Find the function to reference. Search the Blueprint's class hierarchy
	// for the event function.
	UClass* BPClass = Blueprint->GeneratedClass;
	if (!BPClass)
	{
		BPClass = Blueprint->ParentClass;
	}

	UFunction* EventFunc = nullptr;
	if (BPClass)
	{
		EventFunc = BPClass->FindFunctionByName(FName(*EventName));
	}

	// Create the event node.
	FGraphNodeCreator<UK2Node_Event> NodeCreator(*EventGraph);
	UK2Node_Event* EventNode = NodeCreator.CreateNode();

	if (EventFunc)
	{
		// Set up as an override of an existing function.
		EventNode->EventReference.SetFromField<UFunction>(EventFunc, false);
		EventNode->bOverrideFunction = true;
	}
	else
	{
		// Custom event — set the name directly.
		EventNode->CustomFunctionName = FName(*EventName);
	}

	EventNode->NodePosX = 0;
	EventNode->NodePosY = 0;

	NodeCreator.Finalize();

	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

	FString NodeId = NodeIdToString(EventNode->NodeGuid);
	UE_LOG(LogPyUnreal, Log, TEXT("AddEventNode: Created '%s' (ID: %s) in '%s'"),
		*EventName, *NodeId, *Blueprint->GetName());

	return NodeId;
}


// =============================================================================
// Add Function Call Node
// =============================================================================

FString UPyUnrealBlueprintLibrary::AddFunctionCallNode(
	UBlueprint* Blueprint,
	const FString& FunctionName,
	const FString& TargetClass)
{
	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddFunctionCallNode: Blueprint is null"));
		return FString();
	}

	UEdGraph* EventGraph = GetEventGraph(Blueprint);
	if (!EventGraph)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddFunctionCallNode: No EventGraph found in '%s'"),
			*Blueprint->GetName());
		return FString();
	}

	// Find the target class to look up the function.
	UClass* FuncOwnerClass = nullptr;

	if (!TargetClass.IsEmpty())
	{
		// Search for the class by name.
		FuncOwnerClass = FindObject<UClass>(ANY_PACKAGE, *TargetClass);
		if (!FuncOwnerClass)
		{
			// Try with prefix variations (AActor, UObject, etc.).
			FString WithPrefix = FString::Printf(TEXT("A%s"), *TargetClass);
			FuncOwnerClass = FindObject<UClass>(ANY_PACKAGE, *WithPrefix);
		}
		if (!FuncOwnerClass)
		{
			FString WithPrefix = FString::Printf(TEXT("U%s"), *TargetClass);
			FuncOwnerClass = FindObject<UClass>(ANY_PACKAGE, *WithPrefix);
		}
	}
	else
	{
		// Use the Blueprint's own class.
		FuncOwnerClass = Blueprint->GeneratedClass;
		if (!FuncOwnerClass)
		{
			FuncOwnerClass = Blueprint->ParentClass;
		}
	}

	// Find the function.
	UFunction* Function = nullptr;
	if (FuncOwnerClass)
	{
		Function = FuncOwnerClass->FindFunctionByName(FName(*FunctionName));
	}

	// If not found on the explicit class, search common engine classes.
	if (!Function)
	{
		// Try common base classes where these functions live.
		TArray<UClass*> SearchClasses;
		SearchClasses.Add(AActor::StaticClass());
		SearchClasses.Add(APawn::StaticClass());
		SearchClasses.Add(UObject::StaticClass());

		// Also search KismetMathLibrary and KismetSystemLibrary for math/utility.
		UClass* MathLib = FindObject<UClass>(ANY_PACKAGE, TEXT("KismetMathLibrary"));
		if (MathLib) SearchClasses.Add(MathLib);
		UClass* SysLib = FindObject<UClass>(ANY_PACKAGE, TEXT("KismetSystemLibrary"));
		if (SysLib) SearchClasses.Add(SysLib);

		for (UClass* SearchClass : SearchClasses)
		{
			Function = SearchClass->FindFunctionByName(FName(*FunctionName));
			if (Function)
			{
				FuncOwnerClass = SearchClass;
				break;
			}
		}
	}

	if (!Function)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("AddFunctionCallNode: Function '%s' not found (target class: '%s')"),
			*FunctionName, *TargetClass);
		return FString();
	}

	FScopedTransaction Transaction(FText::FromString(
		FString::Printf(TEXT("PyUnreal: Add Call '%s'"), *FunctionName)));

	EventGraph->Modify();

	// Create the function call node.
	FGraphNodeCreator<UK2Node_CallFunction> NodeCreator(*EventGraph);
	UK2Node_CallFunction* CallNode = NodeCreator.CreateNode();

	// Set the function reference.
	CallNode->FunctionReference.SetFromField<UFunction>(Function, false);

	CallNode->NodePosX = 0;
	CallNode->NodePosY = 0;

	NodeCreator.Finalize();

	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

	FString NodeId = NodeIdToString(CallNode->NodeGuid);
	UE_LOG(LogPyUnreal, Log,
		TEXT("AddFunctionCallNode: Created call to '%s::%s' (ID: %s)"),
		*FuncOwnerClass->GetName(), *FunctionName, *NodeId);

	return NodeId;
}


// =============================================================================
// Add Cast Node
// =============================================================================

FString UPyUnrealBlueprintLibrary::AddCastNode(
	UBlueprint* Blueprint,
	const FString& TargetClassName)
{
	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddCastNode: Blueprint is null"));
		return FString();
	}

	UEdGraph* EventGraph = GetEventGraph(Blueprint);
	if (!EventGraph)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddCastNode: No EventGraph found"));
		return FString();
	}

	// Find the target class.
	UClass* TargetClass = FindObject<UClass>(ANY_PACKAGE, *TargetClassName);

	// Try with common prefixes if not found.
	if (!TargetClass)
	{
		TargetClass = FindObject<UClass>(ANY_PACKAGE,
			*FString::Printf(TEXT("A%s"), *TargetClassName));
	}
	if (!TargetClass)
	{
		TargetClass = FindObject<UClass>(ANY_PACKAGE,
			*FString::Printf(TEXT("U%s"), *TargetClassName));
	}
	// Try loading as a Blueprint class (for game-specific BP classes).
	if (!TargetClass)
	{
		// Search the asset registry for a Blueprint with this name.
		FString SearchName = TargetClassName;
		// Check common Blueprint paths.
		UObject* BPAsset = StaticLoadObject(UBlueprint::StaticClass(), nullptr,
			*FString::Printf(TEXT("/Game/%s.%s"), *SearchName, *SearchName));
		if (UBlueprint* LoadedBP = Cast<UBlueprint>(BPAsset))
		{
			TargetClass = LoadedBP->GeneratedClass;
		}
	}

	if (!TargetClass)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("AddCastNode: Class '%s' not found"), *TargetClassName);
		return FString();
	}

	FScopedTransaction Transaction(FText::FromString(
		FString::Printf(TEXT("PyUnreal: Add Cast to '%s'"), *TargetClassName)));

	EventGraph->Modify();

	// Create the dynamic cast node.
	FGraphNodeCreator<UK2Node_DynamicCast> NodeCreator(*EventGraph);
	UK2Node_DynamicCast* CastNode = NodeCreator.CreateNode();

	CastNode->TargetType = TargetClass;

	CastNode->NodePosX = 0;
	CastNode->NodePosY = 0;

	NodeCreator.Finalize();

	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

	FString NodeId = NodeIdToString(CastNode->NodeGuid);
	UE_LOG(LogPyUnreal, Log,
		TEXT("AddCastNode: Created cast to '%s' (ID: %s)"),
		*TargetClass->GetName(), *NodeId);

	return NodeId;
}


// =============================================================================
// Add Variable Get/Set Nodes
// =============================================================================

FString UPyUnrealBlueprintLibrary::AddVariableGetNode(
	UBlueprint* Blueprint,
	const FString& VarName)
{
	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddVariableGetNode: Blueprint is null"));
		return FString();
	}

	UEdGraph* EventGraph = GetEventGraph(Blueprint);
	if (!EventGraph)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddVariableGetNode: No EventGraph found"));
		return FString();
	}

	FScopedTransaction Transaction(FText::FromString(
		FString::Printf(TEXT("PyUnreal: Add Get '%s'"), *VarName)));

	EventGraph->Modify();

	// Create the variable GET node.
	FGraphNodeCreator<UK2Node_VariableGet> NodeCreator(*EventGraph);
	UK2Node_VariableGet* GetNode = NodeCreator.CreateNode();

	// Set the variable reference. The variable lives on the Blueprint's
	// generated class (self context).
	GetNode->VariableReference.SetSelfMember(FName(*VarName));

	GetNode->NodePosX = 0;
	GetNode->NodePosY = 0;

	NodeCreator.Finalize();

	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

	FString NodeId = NodeIdToString(GetNode->NodeGuid);
	UE_LOG(LogPyUnreal, Log,
		TEXT("AddVariableGetNode: Created GET '%s' (ID: %s)"),
		*VarName, *NodeId);

	return NodeId;
}


FString UPyUnrealBlueprintLibrary::AddVariableSetNode(
	UBlueprint* Blueprint,
	const FString& VarName)
{
	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddVariableSetNode: Blueprint is null"));
		return FString();
	}

	UEdGraph* EventGraph = GetEventGraph(Blueprint);
	if (!EventGraph)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("AddVariableSetNode: No EventGraph found"));
		return FString();
	}

	FScopedTransaction Transaction(FText::FromString(
		FString::Printf(TEXT("PyUnreal: Add Set '%s'"), *VarName)));

	EventGraph->Modify();

	// Create the variable SET node.
	FGraphNodeCreator<UK2Node_VariableSet> NodeCreator(*EventGraph);
	UK2Node_VariableSet* SetNode = NodeCreator.CreateNode();

	// Set the variable reference (self member).
	SetNode->VariableReference.SetSelfMember(FName(*VarName));

	SetNode->NodePosX = 0;
	SetNode->NodePosY = 0;

	NodeCreator.Finalize();

	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

	FString NodeId = NodeIdToString(SetNode->NodeGuid);
	UE_LOG(LogPyUnreal, Log,
		TEXT("AddVariableSetNode: Created SET '%s' (ID: %s)"),
		*VarName, *NodeId);

	return NodeId;
}


// =============================================================================
// Connect Pins
// =============================================================================

bool UPyUnrealBlueprintLibrary::ConnectPins(
	UBlueprint* Blueprint,
	const FString& SourceNodeId,
	const FString& SourcePin,
	const FString& TargetNodeId,
	const FString& TargetPin)
{
	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("ConnectPins: Blueprint is null"));
		return false;
	}

	// Find the source and target nodes.
	UEdGraphNode* SourceNode = FindNodeById(Blueprint, SourceNodeId);
	UEdGraphNode* TargetNode = FindNodeById(Blueprint, TargetNodeId);

	if (!SourceNode)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("ConnectPins: Source node '%s' not found"), *SourceNodeId);
		return false;
	}
	if (!TargetNode)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("ConnectPins: Target node '%s' not found"), *TargetNodeId);
		return false;
	}

	// Find the output pin on the source node.
	UEdGraphPin* OutPin = nullptr;
	for (UEdGraphPin* Pin : SourceNode->Pins)
	{
		if (Pin->Direction == EGPD_Output && Pin->PinName.ToString() == SourcePin)
		{
			OutPin = Pin;
			break;
		}
	}

	// Find the input pin on the target node.
	UEdGraphPin* InPin = nullptr;
	for (UEdGraphPin* Pin : TargetNode->Pins)
	{
		if (Pin->Direction == EGPD_Input && Pin->PinName.ToString() == TargetPin)
		{
			InPin = Pin;
			break;
		}
	}

	if (!OutPin)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("ConnectPins: Output pin '%s' not found on source node"), *SourcePin);
		return false;
	}
	if (!InPin)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("ConnectPins: Input pin '%s' not found on target node"), *TargetPin);
		return false;
	}

	FScopedTransaction Transaction(FText::FromString(
		FString::Printf(TEXT("PyUnreal: Connect %s.%s -> %s.%s"),
			*SourceNodeId.Left(8), *SourcePin,
			*TargetNodeId.Left(8), *TargetPin)));

	// Use the schema to make the connection — this validates pin compatibility.
	const UEdGraphSchema_K2* Schema = GetDefault<UEdGraphSchema_K2>();
	bool bConnected = Schema->TryCreateConnection(OutPin, InPin);

	if (bConnected)
	{
		FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

		UE_LOG(LogPyUnreal, Log,
			TEXT("ConnectPins: Connected '%s' -> '%s'"),
			*SourcePin, *TargetPin);
	}
	else
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("ConnectPins: Schema rejected connection '%s' -> '%s' (type mismatch?)"),
			*SourcePin, *TargetPin);
	}

	return bConnected;
}


// =============================================================================
// Get Node Pins
// =============================================================================

bool UPyUnrealBlueprintLibrary::GetNodePins(
	UBlueprint* Blueprint,
	const FString& NodeId,
	TArray<FString>& OutPins)
{
	OutPins.Empty();

	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("GetNodePins: Blueprint is null"));
		return false;
	}

	UEdGraphNode* Node = FindNodeById(Blueprint, NodeId);
	if (!Node)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("GetNodePins: Node '%s' not found"), *NodeId);
		return false;
	}

	// Build pin descriptions: "Direction:PinName:PinType"
	for (UEdGraphPin* Pin : Node->Pins)
	{
		// Skip hidden pins.
		if (Pin->bHidden)
		{
			continue;
		}

		FString Direction = (Pin->Direction == EGPD_Input) ? TEXT("In") : TEXT("Out");
		FString PinName = Pin->PinName.ToString();
		FString PinType = Pin->PinType.PinCategory.ToString();

		// Add subcategory for more specific type info.
		if (!Pin->PinType.PinSubCategory.IsNone())
		{
			PinType += TEXT(".") + Pin->PinType.PinSubCategory.ToString();
		}
		// Add object type for struct/object pins.
		if (Pin->PinType.PinSubCategoryObject.IsValid())
		{
			PinType += TEXT(":") + Pin->PinType.PinSubCategoryObject->GetName();
		}

		OutPins.Add(FString::Printf(TEXT("%s:%s:%s"), *Direction, *PinName, *PinType));
	}

	return true;
}


// =============================================================================
// Set Node Position
// =============================================================================

bool UPyUnrealBlueprintLibrary::SetNodePosition(
	UBlueprint* Blueprint,
	const FString& NodeId,
	int32 X,
	int32 Y)
{
	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("SetNodePosition: Blueprint is null"));
		return false;
	}

	UEdGraphNode* Node = FindNodeById(Blueprint, NodeId);
	if (!Node)
	{
		UE_LOG(LogPyUnreal, Error,
			TEXT("SetNodePosition: Node '%s' not found"), *NodeId);
		return false;
	}

	Node->NodePosX = X;
	Node->NodePosY = Y;

	return true;
}


// =============================================================================
// List EventGraph Nodes
// =============================================================================

bool UPyUnrealBlueprintLibrary::ListEventGraphNodes(
	UBlueprint* Blueprint,
	TArray<FString>& OutNodes)
{
	OutNodes.Empty();

	if (!Blueprint)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("ListEventGraphNodes: Blueprint is null"));
		return false;
	}

	UEdGraph* EventGraph = GetEventGraph(Blueprint);
	if (!EventGraph)
	{
		UE_LOG(LogPyUnreal, Error, TEXT("ListEventGraphNodes: No EventGraph found"));
		return false;
	}

	for (UEdGraphNode* Node : EventGraph->Nodes)
	{
		if (!Node)
		{
			continue;
		}

		FString NodeId = NodeIdToString(Node->NodeGuid);
		FString ClassName = Node->GetClass()->GetName();
		FString Title = Node->GetNodeTitle(ENodeTitleType::ListView).ToString();

		OutNodes.Add(FString::Printf(TEXT("%s:%s:%s"), *NodeId, *ClassName, *Title));
	}

	return true;
}
