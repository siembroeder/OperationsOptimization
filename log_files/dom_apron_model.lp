\ Model Apron
\ LP format - for model browsing. Use MPS format to capture full model detail.
\ Signature: 0xe514800ceacd7d3f
Maximize
  z_0_1 + z_0_2 + z_0_3 + z_0_4 + z_0_5 + z_0_6 + z_0_7 + z_0_8 + z_0_9
   + z_1_10 + z_2_10 + z_3_10 + z_4_10 + z_5_10 + z_6_10 + z_7_10 + z_8_10
   + z_9_10 + z_1_5 + z_1_6 + z_1_7 + z_1_8 + z_1_9 + z_2_5 + z_2_6 + z_2_7
   + z_2_8 + z_2_9 + z_3_5 + z_3_6 + z_3_7 + z_3_8 + z_3_9 + z_4_6 + z_4_8
   + z_4_9
Subject To
 flowUnitsSource: z_0_1 + z_0_2 + z_0_3 + z_0_4 + z_0_5 + z_0_6 + z_0_7
   + z_0_8 + z_0_9 <= 3
 flowUnitsSink: z_1_10 + z_2_10 + z_3_10 + z_4_10 + z_5_10 + z_6_10
   + z_7_10 + z_8_10 + z_9_10 <= 3
 flowConservationNode_1: - z_0_1 + z_1_10 + z_1_5 + z_1_6 + z_1_7 + z_1_8
   + z_1_9 = 0
 oneOutgoingNode_1: z_1_10 + z_1_5 + z_1_6 + z_1_7 + z_1_8 + z_1_9 <= 1
 flowConservationNode_2: - z_0_2 + z_2_10 + z_2_5 + z_2_6 + z_2_7 + z_2_8
   + z_2_9 = 0
 oneOutgoingNode_2: z_2_10 + z_2_5 + z_2_6 + z_2_7 + z_2_8 + z_2_9 <= 1
 flowConservationNode_3: - z_0_3 + z_3_10 + z_3_5 + z_3_6 + z_3_7 + z_3_8
   + z_3_9 = 0
 oneOutgoingNode_3: z_3_10 + z_3_5 + z_3_6 + z_3_7 + z_3_8 + z_3_9 <= 1
 flowConservationNode_4: - z_0_4 + z_4_10 + z_4_6 + z_4_8 + z_4_9 = 0
 oneOutgoingNode_4: z_4_10 + z_4_6 + z_4_8 + z_4_9 <= 1
 flowConservationNode_5: - z_0_5 + z_5_10 - z_1_5 - z_2_5 - z_3_5 = 0
 oneOutgoingNode_5: z_5_10 <= 1
 flowConservationNode_6: - z_0_6 + z_6_10 - z_1_6 - z_2_6 - z_3_6 - z_4_6
   = 0
 oneOutgoingNode_6: z_6_10 <= 1
 flowConservationNode_7: - z_0_7 + z_7_10 - z_1_7 - z_2_7 - z_3_7 = 0
 oneOutgoingNode_7: z_7_10 <= 1
 flowConservationNode_8: - z_0_8 + z_8_10 - z_1_8 - z_2_8 - z_3_8 - z_4_8
   = 0
 oneOutgoingNode_8: z_8_10 <= 1
 flowConservationNode_9: - z_0_9 + z_9_10 - z_1_9 - z_2_9 - z_3_9 - z_4_9
   = 0
 oneOutgoingNode_9: z_9_10 <= 1
Bounds
Binaries
 z_0_1 z_0_2 z_0_3 z_0_4 z_0_5 z_0_6 z_0_7 z_0_8 z_0_9 z_1_10 z_2_10 z_3_10
 z_4_10 z_5_10 z_6_10 z_7_10 z_8_10 z_9_10 z_1_5 z_1_6 z_1_7 z_1_8 z_1_9
 z_2_5 z_2_6 z_2_7 z_2_8 z_2_9 z_3_5 z_3_6 z_3_7 z_3_8 z_3_9 z_4_6 z_4_8
 z_4_9
End
