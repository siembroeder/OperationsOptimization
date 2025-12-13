\ Model Apron
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xbba403918ac4bd96
Maximize
  z_0_1 + z_0_2 + z_0_3 + z_0_4 + z_0_5 + z_0_6 + z_0_7 + z_0_8 + z_1_9
   + z_2_9 + z_3_9 + z_4_9 + z_5_9 + z_6_9 + z_7_9 + z_8_9 + z_1_5 + z_1_6
   + z_1_7 + z_1_8 + z_2_5 + z_2_6 + z_2_7 + z_2_8 + z_3_5 + z_3_6 + z_3_7
   + z_3_8 + z_4_6 + z_4_8
Subject To
 flowUnitsSource: z_0_1 + z_0_2 + z_0_3 + z_0_4 + z_0_5 + z_0_6 + z_0_7
   + z_0_8 <= 3
 flowUnitsSink: z_1_9 + z_2_9 + z_3_9 + z_4_9 + z_5_9 + z_6_9 + z_7_9
   + z_8_9 <= 3
 flowConservationNode_1: - z_0_1 + z_1_9 + z_1_5 + z_1_6 + z_1_7 + z_1_8
   = 0
 oneOutgoingNode_1: z_1_9 + z_1_5 + z_1_6 + z_1_7 + z_1_8 <= 1
 flowConservationNode_2: - z_0_2 + z_2_9 + z_2_5 + z_2_6 + z_2_7 + z_2_8
   = 0
 oneOutgoingNode_2: z_2_9 + z_2_5 + z_2_6 + z_2_7 + z_2_8 <= 1
 flowConservationNode_3: - z_0_3 + z_3_9 + z_3_5 + z_3_6 + z_3_7 + z_3_8
   = 0
 oneOutgoingNode_3: z_3_9 + z_3_5 + z_3_6 + z_3_7 + z_3_8 <= 1
 flowConservationNode_4: - z_0_4 + z_4_9 + z_4_6 + z_4_8 = 0
 oneOutgoingNode_4: z_4_9 + z_4_6 + z_4_8 <= 1
 flowConservationNode_5: - z_0_5 + z_5_9 - z_1_5 - z_2_5 - z_3_5 = 0
 oneOutgoingNode_5: z_5_9 <= 1
 flowConservationNode_6: - z_0_6 + z_6_9 - z_1_6 - z_2_6 - z_3_6 - z_4_6
   = 0
 oneOutgoingNode_6: z_6_9 <= 1
 flowConservationNode_7: - z_0_7 + z_7_9 - z_1_7 - z_2_7 - z_3_7 = 0
 oneOutgoingNode_7: z_7_9 <= 1
 flowConservationNode_8: - z_0_8 + z_8_9 - z_1_8 - z_2_8 - z_3_8 - z_4_8
   = 0
 oneOutgoingNode_8: z_8_9 <= 1
Bounds
Binaries
 z_0_1 z_0_2 z_0_3 z_0_4 z_0_5 z_0_6 z_0_7 z_0_8 z_1_9 z_2_9 z_3_9 z_4_9
 z_5_9 z_6_9 z_7_9 z_8_9 z_1_5 z_1_6 z_1_7 z_1_8 z_2_5 z_2_6 z_2_7 z_2_8
 z_3_5 z_3_6 z_3_7 z_3_8 z_4_6 z_4_8
End
