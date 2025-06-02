from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

examples = [
    {
        "Context": "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms that can learn and make decisions from data. There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled data to train models, where the algorithm learns from input-output pairs. Common supervised learning tasks include classification and regression. Unsupervised learning works with unlabeled data to find hidden patterns or structures. Clustering and dimensionality reduction are typical unsupervised learning techniques. Reinforcement learning involves an agent learning to make decisions by interacting with an environment and receiving rewards or penalties. This approach is commonly used in game playing, robotics, and autonomous systems. Each type of machine learning has its own strengths and is suitable for different types of problems and applications.",
        "Main_Points": "1. Introduction to Machine Learning\n   - Definition as subset of AI\n   - Focus on algorithms that learn from data\n\n2. Supervised Learning\n   - Uses labeled data for training\n   - Learns from input-output pairs\n   - Applications: classification and regression\n\n3. Unsupervised Learning\n   - Works with unlabeled data\n   - Discovers hidden patterns and structures\n   - Techniques: clustering and dimensionality reduction\n\n4. Reinforcement Learning\n   - Agent learns through environment interaction\n   - Uses reward/penalty system\n   - Applications: gaming, robotics, autonomous systems\n\n5. Comparative Analysis\n   - Each type has unique strengths\n   - Suitable for different problem domains"
    },
    {
        "Context": "Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, scientific evidence shows that human activities have been the primary driver of climate change since the 1800s. The main cause is the burning of fossil fuels like coal, oil, and gas, which releases greenhouse gases into the atmosphere. These gases trap heat from the sun, causing global temperatures to rise. The effects of climate change are widespread and include rising sea levels, more frequent extreme weather events, changes in precipitation patterns, and impacts on ecosystems and biodiversity. Melting ice sheets and glaciers contribute to sea level rise, threatening coastal communities worldwide. Extreme weather events such as hurricanes, droughts, and floods are becoming more intense and frequent. Agriculture is also affected, with changing growing seasons and crop yields. To address climate change, both mitigation and adaptation strategies are necessary. Mitigation involves reducing greenhouse gas emissions through renewable energy, energy efficiency, and sustainable practices. Adaptation involves preparing for and adjusting to the effects of climate change that are already occurring or inevitable.",
        "Main_Points": "1. Definition and Causes of Climate Change\n   - Long-term shifts in global temperatures and weather\n   - Human activities as primary driver since 1800s\n   - Fossil fuel burning releases greenhouse gases\n\n2. Greenhouse Effect Mechanism\n   - Greenhouse gases trap solar heat\n   - Results in global temperature rise\n\n3. Environmental Impacts\n   - Rising sea levels from melting ice\n   - Threats to coastal communities\n   - Ecosystem and biodiversity changes\n\n4. Extreme Weather Events\n   - Increased frequency and intensity\n   - Hurricanes, droughts, and floods\n   - Changing precipitation patterns\n\n5. Agricultural Effects\n   - Altered growing seasons\n   - Variable crop yields\n   - Food security implications\n\n6. Response Strategies\n   - Mitigation: reducing emissions through renewables\n   - Adaptation: preparing for inevitable changes\n   - Sustainable practices implementation"
    },
    {
        "Context": "The human digestive system is a complex network of organs that work together to break down food, absorb nutrients, and eliminate waste. The process begins in the mouth, where food is mechanically broken down by chewing and chemically broken down by saliva enzymes. From the mouth, food travels down the esophagus to the stomach through a process called peristalsis. In the stomach, gastric juices containing hydrochloric acid and pepsin further break down proteins. The partially digested food, now called chyme, moves into the small intestine. The small intestine is where most nutrient absorption occurs. It has three sections: the duodenum, jejunum, and ileum. The pancreas and liver play crucial roles by producing digestive enzymes and bile respectively. The large intestine, or colon, is responsible for water absorption and forming solid waste. Finally, waste is eliminated through the rectum and anus. The entire digestive process typically takes 24-72 hours from ingestion to elimination.",
        "Main_Points": "1. Digestive System Overview\n   - Complex network of interconnected organs\n   - Functions: breakdown, absorption, elimination\n\n2. Oral Processing\n   - Mechanical breakdown through chewing\n   - Chemical breakdown via saliva enzymes\n\n3. Esophageal Transport\n   - Food movement through peristalsis\n   - Connection between mouth and stomach\n\n4. Gastric Processing\n   - Gastric juice action (HCl and pepsin)\n   - Protein breakdown and chyme formation\n\n5. Small Intestine Function\n   - Primary site of nutrient absorption\n   - Three sections: duodenum, jejunum, ileum\n   - Pancreatic enzymes and liver bile support\n\n6. Large Intestine Processing\n   - Water absorption from remaining material\n   - Solid waste formation\n\n7. Waste Elimination\n   - Final removal through rectum and anus\n   - Complete process duration: 24-72 hours"
    }
]

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=ChatPromptTemplate.from_messages([
                    ("user", "Context: {Context}"),
                    ("ai", "Main Points:\n{Main_Points}")
                  ]),
    examples=examples
)

SummarizerMainPointPrompt = ChatPromptTemplate.from_messages([
    ("system", """
                       "/no_think"
                       You are an expert content summarization assistant designed to create structured, comprehensive main points and table of contents from transcripts and PDF documents. Your purpose is to help users quickly understand and navigate complex content by identifying and organizing key information.

                        ## Core Objectives:

                        1. Extract and organize main points from any given content
                        2. Create clear, hierarchical structure resembling a table of contents
                        3. Maintain logical flow and relationships between concepts
                        4. Ensure comprehensive coverage of important topics
                        5. Present information in an easily scannable format

                        ## Content Analysis Guidelines:

                        ### Information Identification:
                            - Identify major themes, concepts, and topics
                            - Recognize supporting details and sub-concepts
                            - Distinguish between primary and secondary information
                            - Note relationships and connections between ideas
                            - Capture key processes, procedures, or methodologies
                            - Include important definitions, examples, or case studies

                        ### Structural Organization:
                            - Create hierarchical numbering system (1, 2, 3... with sub-points)
                            - Group related concepts under appropriate main headings
                            - Maintain logical sequence and flow of ideas
                            - Use clear, descriptive headings that capture essence of content
                            - Include relevant sub-points that provide important details
                            - Ensure each main point represents a distinct concept or theme

                        ## Output Format Requirements:

                        ### Main Points Structure:
                            - Use numbered main points (1, 2, 3...)
                            - Include descriptive sub-points with bullet formatting
                            - Maintain consistent indentation and spacing
                            - Keep language clear, concise, and professional
                            - Use present tense and active voice when possible
                            - Avoid redundancy while ensuring completeness

                        ### Quality Standards:
                            - Capture 95%+ of important information from source
                            - Maintain accuracy and context of original content
                            - Create standalone understanding without requiring source reference
                            - Balance comprehensiveness with readability
                            - Ensure each point adds unique value
                            - Use terminology consistent with source material

                        ## Content Processing Approach:

                        1. First Pass: Identify major themes and primary concepts
                        2. Second Pass: Organize supporting details and relationships
                        3. Third Pass: Structure information hierarchically
                        4. Final Pass: Refine language and ensure clarity

                        ## Formatting Guidelines:

                        - Use clear, descriptive headings
                        - Maintain consistent formatting throughout
                        - Include specific details that add value
                        - Group related sub-points logically
                        - Ensure parallel structure in similar points
                        - Balance detail level across all main points

                        Example:
                     """),
     few_shot_prompt,
     ("user", "Context: {context}")
])